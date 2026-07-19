#!/usr/bin/env python3
"""Reproduce a Delta column-mapping protocol gate without Databricks or Ray."""

from __future__ import annotations

import json
import tempfile
import time
import uuid
from pathlib import Path

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from deltalake import DeltaTable
from deltalake.exceptions import DeltaProtocolError

LOGICAL_NAME = "customer_score"
PHYSICAL_NAME = "col-4d014c4b-7d15-4d7b-a89e-40dfdca76a22"
VALUES = [1.5, 2.5]


def _write_json_lines(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def create_column_mapped_table(root: Path) -> Path:
    """Create a minimal name-mapping mechanism fixture.

    The Parquet writer doesn't encode Delta's required field_id. That doesn't
    affect these narrow checks: name mode resolves by physical name, and
    deltalake rejects reader protocol v2 before scanning the file.
    """
    root.mkdir()
    log_dir = root / "_delta_log"
    log_dir.mkdir()

    parquet_path = root / "part-00000.parquet"
    pq.write_table(pa.table({PHYSICAL_NAME: VALUES}), parquet_path)

    schema = {
        "type": "struct",
        "fields": [
            {
                "name": LOGICAL_NAME,
                "type": "double",
                "nullable": True,
                "metadata": {
                    "delta.columnMapping.id": 1,
                    "delta.columnMapping.physicalName": PHYSICAL_NAME,
                },
            }
        ],
    }
    stats = {
        "numRecords": len(VALUES),
        "minValues": {PHYSICAL_NAME: min(VALUES)},
        "maxValues": {PHYSICAL_NAME: max(VALUES)},
        "nullCount": {PHYSICAL_NAME: 0},
    }
    now_ms = int(time.time() * 1000)
    records: list[dict[str, object]] = [
        {"protocol": {"minReaderVersion": 2, "minWriterVersion": 5}},
        {
            "metaData": {
                "id": str(uuid.uuid4()),
                "format": {"provider": "parquet", "options": {}},
                "schemaString": json.dumps(schema, separators=(",", ":")),
                "partitionColumns": [],
                "configuration": {
                    "delta.columnMapping.mode": "name",
                    "delta.columnMapping.maxColumnId": "1",
                },
                "createdTime": now_ms,
            }
        },
        {
            "add": {
                "path": parquet_path.name,
                "partitionValues": {},
                "size": parquet_path.stat().st_size,
                "modificationTime": now_ms,
                "dataChange": True,
                "stats": json.dumps(stats, separators=(",", ":")),
            }
        },
    ]
    _write_json_lines(log_dir / "00000000000000000000.json", records)
    return root


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ray-64854-") as temp_dir:
        table_path = create_column_mapped_table(Path(temp_dir) / "table")
        delta_table = DeltaTable(str(table_path))

        raw_dataset = ds.dataset(delta_table.file_uris(), format="parquet")
        raw_names = raw_dataset.schema.names

        print(f"raw file schema: {raw_names}")
        print(f"delta schema: {delta_table.schema().to_arrow().names}")

        assert raw_names == [PHYSICAL_NAME]
        assert delta_table.schema().to_arrow().names == [LOGICAL_NAME]

        try:
            delta_table.to_pyarrow_dataset()
        except DeltaProtocolError as error:
            error_message = str(error)
            print(f"unified dataset error: {error_message}")
            assert "minimum reader version is 2" in error_message
            assert "only supports version 1 or 3" in error_message
        else:
            raise AssertionError(
                "deltalake 1.6.1 unexpectedly accepted the column-mapped table"
            )

        print(
            "PASS: the old raw-file path exposes the physical name, while the "
            "current unified path fails explicitly"
        )


if __name__ == "__main__":
    main()
