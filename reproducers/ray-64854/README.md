# Ray Data #64854 column-mapping reproducer

This fixture isolates the behavior reported in
[ray-project/ray#64854](https://github.com/ray-project/ray/issues/64854)
without requiring Databricks, cloud storage, or a Ray cluster.

It creates a minimal protocol-gate/mechanism fixture:

- one Parquet file with a UUID-style physical column name;
- one Delta transaction-log commit using name-based column mapping;
- a logical Delta schema mapping that physical name to `customer_score`.

It then compares:

1. the raw Parquet dataset assembled from `DeltaTable.file_uris()`, matching
   Ray 2.55.1's `read_delta` path;
2. `DeltaTable.to_pyarrow_dataset()`, matching current Ray master.

## Run

From the tracker repository root, use an isolated environment with the versions
from the report:

```sh
python -m venv /tmp/ray-64854-venv
/tmp/ray-64854-venv/bin/pip install "deltalake==1.6.1" "pyarrow==21.0.0"
/tmp/ray-64854-venv/bin/python reproducers/ray-64854/reproduce.py
```

Expected result with `deltalake==1.6.1`:

```text
raw file schema: ['col-4d014c4b-7d15-4d7b-a89e-40dfdca76a22']
delta schema: ['customer_score']
unified dataset error: The table's minimum reader version is 2 but deltalake only supports ...
PASS: the old raw-file path exposes the physical name, while the current unified path fails explicitly
```

This demonstrates two distinct states:

- Ray 2.55.1's raw-file path bypasses the Delta protocol check and exposes
  physical UUID names.
- Current Ray master delegates to `to_pyarrow_dataset()`, which rejects this
  unsupported reader protocol instead of silently returning the wrong schema.

The current path is safer, but it does not add column-mapping support. That
requires support in delta-rs (or another Delta reader), not a Ray-side rename
applied after Parquet discovery.

## Fixture limitation

The plain PyArrow writer doesn't encode Delta's required column `field_id` in
the Parquet schema. This fixture is therefore not a fully protocol-conforming
writer output. It is sufficient for the two assertions it makes:

- raw Parquet discovery exposes the physical name in name-mapping mode, where
  readers resolve by `delta.columnMapping.physicalName`, not by field ID;
- deltalake 1.6.1 rejects reader protocol v2 before scanning the Parquet file.

The script uses `TemporaryDirectory`; it leaves no generated table behind.
