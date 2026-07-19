#!/usr/bin/env python3
"""Reproduce Dask #12507 across isolated Python hash seeds."""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import os
import subprocess
import sys
from pathlib import Path


def build_selected_array():
    """Build the deterministic sliced array from the issue report."""
    import dask.array as da
    import numpy as np
    from dask import delayed

    def ident(block):
        return block

    def read(i, j, t):
        block_value = t * 10_000 + i * 100 + j
        return np.full((512, 512), block_value, dtype=float)

    nt, ny, nx = 8, 10, 20
    times = []
    for t in range(nt):
        rows = []
        for i in range(ny):
            row = [
                da.from_delayed(
                    delayed(read)(
                        i,
                        j,
                        t,
                        dask_key_name=f"read-{t}-{i}-{j}",
                    ),
                    (512, 512),
                    dtype=float,
                )
                for j in range(nx)
            ]
            rows.append(da.concatenate(row, axis=1))
        times.append(da.concatenate(rows, axis=0)[None])

    source = da.concatenate(times, axis=0)
    overlapped = source.map_overlap(
        ident,
        depth={1: 8, 2: 8},
        boundary="none",
    )
    rechunked = overlapped.rechunk((nt, 512, 512))
    return rechunked[:, :100, :100]


def optimized_task_count() -> int:
    """Build and optimize the deterministic graph from the issue report."""
    import dask

    selected = build_selected_array()
    (optimized,) = dask.optimize(selected)
    return len(optimized.__dask_graph__())


def _stable_toposort_layers(graph) -> list[str]:
    """A deterministic equivalent of HighLevelGraph._toposort_layers()."""
    degree = {
        layer: len(dependencies) for layer, dependencies in graph.dependencies.items()
    }
    reverse_dependencies = {layer: [] for layer in graph.dependencies}
    for layer in sorted(graph.dependencies):
        for dependency in sorted(graph.dependencies[layer]):
            reverse_dependencies[dependency].append(layer)

    ready = [layer for layer, count in degree.items() if count == 0]
    heapq.heapify(ready)
    result = []
    while ready:
        layer = heapq.heappop(ready)
        result.append(layer)
        for dependent in sorted(reverse_dependencies[layer]):
            degree[dependent] -= 1
            if degree[dependent] == 0:
                heapq.heappush(ready, dependent)
    return result


def _filtered_hlg_cull(graph, keys):
    """Experimental cull with per-layer key ownership filtering restored."""
    from dask.base import flatten
    from dask.highlevelgraph import HighLevelGraph
    from dask.tokenize import tokenize

    keys_set = set(flatten(keys))
    if not any(layer.has_legacy_tasks for layer in graph.layers.values()):
        all_external_keys = set()
    else:
        all_external_keys = graph.get_all_external_keys()

    retained_layers = {}
    layer_dependencies = {}
    token = tokenize(keys_set)
    for layer_name in reversed(graph._toposort_layers()):
        layer = graph.layers[layer_name]
        output_keys = keys_set.intersection(layer.get_output_keys())
        if not output_keys:
            continue

        culled_layer, culled_dependencies = layer.cull(
            output_keys,
            all_external_keys,
        )
        if not culled_dependencies:
            continue

        for key, dependencies in culled_dependencies.items():
            keys_set |= dependencies
            keys_set.discard(key)

        new_layer_name = f"{layer_name}-{token}"
        retained_layers[new_layer_name] = culled_layer
        layer_dependencies[new_layer_name] = graph.dependencies[layer_name]

    retained_names = set(retained_layers)
    retained_dependencies = {
        layer_name: layer_dependencies[layer_name] & retained_names
        for layer_name in retained_layers
    }
    return HighLevelGraph(retained_layers, retained_dependencies)


def filtered_optimization_result(*, compute: bool = False) -> dict[str, object]:
    """Run the graph with only the candidate per-layer cull filter applied."""
    import dask
    import numpy as np
    from dask.highlevelgraph import HighLevelGraph

    original_cull = HighLevelGraph.cull
    HighLevelGraph.cull = _filtered_hlg_cull
    try:
        selected = build_selected_array()
        (optimized,) = dask.optimize(selected)
        result: dict[str, object] = {
            "optimized_tasks": len(optimized.__dask_graph__()),
        }
        if compute:
            computed = optimized.compute(
                scheduler="sync",
                optimize_graph=False,
            )
            expected = np.broadcast_to(
                np.arange(8, dtype=float)[:, None, None] * 10_000,
                (8, 100, 100),
            )
            result.update(
                {
                    "computed_shape": list(computed.shape),
                    "computed_dtype": str(computed.dtype),
                    "computed_time_values": computed[:, 0, 0].tolist(),
                    "computed_matches_expected": bool(
                        np.array_equal(computed, expected)
                    ),
                }
            )
        return result
    finally:
        HighLevelGraph.cull = original_cull


def cardinality_fast_path_control() -> dict[str, object]:
    """Show both lower-level cull paths retaining foreign same-sized keys."""
    from dask._task_spec import DataNode
    from dask.highlevelgraph import MaterializedLayer

    owned_keys = {("owned", 0), ("owned", 1)}
    foreign_keys = {("foreign", 0), ("foreign", 1)}

    legacy_layer = MaterializedLayer(
        {
            ("owned", 0): 0,
            ("owned", 1): 1,
        }
    )
    legacy_culled, _ = legacy_layer.cull(foreign_keys, owned_keys)

    task_spec_layer = MaterializedLayer(
        {key: DataNode(key, value) for value, key in enumerate(sorted(owned_keys))}
    )
    task_spec_culled, _ = task_spec_layer.cull(foreign_keys, set())

    return {
        "owned_key_count": len(owned_keys),
        "foreign_key_count": len(foreign_keys),
        "legacy_retained_all_owned": set(legacy_culled) == owned_keys,
        "task_spec_retained_all_owned": set(task_spec_culled) == owned_keys,
    }


def optimization_trace(
    *,
    stable_toposort: bool = False,
) -> dict[str, dict[str, int | str]]:
    """Record where task or layer counts first become seed-dependent."""
    from dask import config
    from dask._task_spec import convert_legacy_graph, fuse_linear_task_spec
    from dask.array.optimization import _optimize_slices
    from dask.blockwise import fuse_roots, optimize_blockwise
    from dask.core import flatten
    from dask.utils import ensure_dict

    selected = build_selected_array()
    keys = list(flatten(selected.__dask_keys__()))
    graph = selected.__dask_graph__()

    def hlg_counts(value) -> dict[str, int | str]:
        dependencies = [
            (str(layer), sorted(str(dependency) for dependency in deps))
            for layer, deps in value.dependencies.items()
        ]
        dependencies.sort()
        fingerprint = hashlib.sha256(
            json.dumps(dependencies, separators=(",", ":")).encode()
        ).hexdigest()
        return {
            "layers": len(value.layers),
            "tasks": len(value),
            "dependency_fingerprint": fingerprint,
        }

    trace = {"raw": hlg_counts(graph)}
    graph = optimize_blockwise(graph, keys=keys)
    trace["after_optimize_blockwise"] = hlg_counts(graph)
    graph = fuse_roots(graph, keys=keys)
    trace["after_fuse_roots"] = hlg_counts(graph)
    if stable_toposort:
        from dask.highlevelgraph import HighLevelGraph

        original_toposort = HighLevelGraph._toposort_layers
        HighLevelGraph._toposort_layers = _stable_toposort_layers
        try:
            graph = graph.cull(set(keys))
        finally:
            HighLevelGraph._toposort_layers = original_toposort
    else:
        graph = graph.cull(set(keys))
    trace["after_cull"] = hlg_counts(graph)

    low_level = convert_legacy_graph(ensure_dict(graph))
    trace["materialized"] = {"layers": 0, "tasks": len(low_level)}
    if config.get("optimization.fuse.active") is not False:
        low_level = fuse_linear_task_spec(low_level, keys=keys)
        trace["after_linear_fusion"] = {"layers": 0, "tasks": len(low_level)}
        low_level = _optimize_slices(low_level)
        trace["after_slice_fusion"] = {"layers": 0, "tasks": len(low_level)}
    return trace


def run_seed(seed: int) -> int:
    """Run one fresh interpreter so PYTHONHASHSEED takes effect."""
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = str(seed)
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--single"],
        check=True,
        capture_output=True,
        env=env,
        text=True,
    )
    result = json.loads(completed.stdout)
    if result["seed"] != str(seed):
        raise RuntimeError(f"subprocess used unexpected seed: {result!r}")
    return int(result["optimized_tasks"])


def summarize(seeds: list[int]) -> dict[str, object]:
    """Run the seed matrix and summarize the graph-size spread."""
    results = {str(seed): run_seed(seed) for seed in seeds}
    counts = list(results.values())
    minimum = min(counts)
    maximum = max(counts)
    return {
        "dask_version": _dask_version(),
        "results": results,
        "unique_task_counts": sorted(set(counts)),
        "minimum_tasks": minimum,
        "maximum_tasks": maximum,
        "max_to_min_ratio": maximum / minimum,
        "hash_seed_changes_graph_size": len(set(counts)) > 1,
    }


def _dask_version() -> str:
    import dask

    return dask.__version__


def main() -> int:
    parser = argparse.ArgumentParser()
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--single",
        action="store_true",
        help="emit one task count in the current interpreter",
    )
    action_group.add_argument(
        "--trace-single",
        action="store_true",
        help="emit optimizer phase counts in the current interpreter",
    )
    action_group.add_argument(
        "--stable-trace-single",
        action="store_true",
        help="trace with a deterministic layer topological order during culling",
    )
    action_group.add_argument(
        "--filtered-single",
        action="store_true",
        help="count tasks with experimental per-layer cull key filtering",
    )
    action_group.add_argument(
        "--filtered-compute-single",
        action="store_true",
        help="also compute the result with experimental per-layer filtering",
    )
    action_group.add_argument(
        "--cardinality-control",
        action="store_true",
        help="demonstrate foreign same-sized keys triggering both cull fast paths",
    )
    parser.add_argument(
        "--expect-fixed",
        action="store_true",
        help="exit successfully only when the seed matrix is invariant",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(range(8)),
        help="hash seeds to compare (default: 0 through 7)",
    )
    args = parser.parse_args()
    if len(set(args.seeds)) != len(args.seeds):
        parser.error("--seeds values must be unique")
    single_action = any(
        (
            args.single,
            args.trace_single,
            args.stable_trace_single,
            args.filtered_single,
            args.filtered_compute_single,
            args.cardinality_control,
        )
    )
    if single_action and args.expect_fixed:
        parser.error("--expect-fixed is only valid in matrix mode")
    if not single_action and len(args.seeds) < 2:
        parser.error("matrix mode requires at least two unique --seeds values")

    if args.single:
        print(
            json.dumps(
                {
                    "seed": os.environ.get("PYTHONHASHSEED"),
                    "optimized_tasks": optimized_task_count(),
                },
                sort_keys=True,
            )
        )
        return 0
    if args.trace_single:
        print(
            json.dumps(
                {
                    "seed": os.environ.get("PYTHONHASHSEED"),
                    "trace": optimization_trace(),
                },
                sort_keys=True,
            )
        )
        return 0
    if args.stable_trace_single:
        print(
            json.dumps(
                {
                    "seed": os.environ.get("PYTHONHASHSEED"),
                    "trace": optimization_trace(stable_toposort=True),
                },
                sort_keys=True,
            )
        )
        return 0
    if args.filtered_single or args.filtered_compute_single:
        print(
            json.dumps(
                {
                    "seed": os.environ.get("PYTHONHASHSEED"),
                    **filtered_optimization_result(
                        compute=args.filtered_compute_single,
                    ),
                },
                sort_keys=True,
            )
        )
        return 0
    if args.cardinality_control:
        print(json.dumps(cardinality_fast_path_control(), sort_keys=True))
        return 0

    summary = summarize(args.seeds)
    print(json.dumps(summary, indent=2, sort_keys=True))
    bug_reproduced = bool(summary["hash_seed_changes_graph_size"])
    if args.expect_fixed and bug_reproduced:
        print(
            "Expected an invariant graph, but task counts changed across seeds.",
            file=sys.stderr,
        )
        return 1
    if not args.expect_fixed and not bug_reproduced:
        print(
            "Expected to reproduce seed-dependent graph sizes, but counts were invariant.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
