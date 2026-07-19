# Dask #12507 reproducer

This is a self-checking adaptation of the public minimal reproducer from
[Dask issue #12507](https://github.com/dask/dask/issues/12507). It constructs a
deterministically keyed array graph, then optimizes it in fresh Python processes
with different `PYTHONHASHSEED` values. Each synthetic input block encodes its
time, row-block, and column-block coordinates so the computation control can
detect selection of the wrong block.

By default, the command succeeds only when at least two seeds produce different
optimized task counts:

```bash
python3 reproduce.py
```

Exit zero therefore means the bug was reproduced; it is not a green upstream
health check. Use `--expect-fixed` after applying a candidate fix to invert that
expectation in matrix mode; combining it with a single-action diagnostic is
rejected. Matrix mode requires at least two unique seeds; duplicate or
single-seed matrices are rejected. Count equality is only a sampled invariant:
use the default matrix or seeds already shown to diverge on the unfixed
baseline. Two buggy seeds that coincidentally have the same count can
false-green.

The original report used Dask 2026.7.1. The default matrix computes no tasks and
downloads no science data; it only constructs and optimizes the graph.

The output records the exact Dask version, count for every seed, unique counts,
minimum and maximum, and the maximum-to-minimum ratio. This proves graph-shape
nondeterminism, but it does not by itself identify which unordered optimizer
traversal causes it.

## Local result

On Dask 2026.7.1, Python 3.11.13, and NumPy 1.26.4, seeds 0 through 7 produced:

```text
seed 0: 728 tasks
seed 1: 428 tasks
seed 2: 502 tasks
seed 3: 502 tasks
seed 4: 658 tasks
seed 5: 472 tasks
seed 6: 708 tasks
seed 7: 334 tasks
```

The maximum-to-minimum ratio was 2.1796. Two additional isolated runs for seed
0 both produced 728 tasks, and two for seed 7 both produced 334 tasks.

Use `--trace-single` in a process with an explicit `PYTHONHASHSEED` to record
task and layer counts after each optimizer phase. Use
`--stable-trace-single` to repeat that trace while replacing only the
high-level graph's layer topological traversal with a deterministic min-heap.
All eight tested seeds then converged to 438 tasks. That experiment localizes
the first task-count and declared layer-topology divergence to culling, but task
representations already differ before that phase. Stable ordering is not a
production fix and does not produce the smallest graph.

`--filtered-single` restores the pre-PR-#11899 behavior of intersecting the
global outstanding keys with each layer's output keys before culling. All eight
seeds then produce 82 tasks without sorting. `--filtered-compute-single` also
computes the selected array; seed 0 and seed 7 both return a `float64` result
with shape `(8, 100, 100)` whose time planes contain the expected encoded values
`0, 10000, ..., 70000`. That compute disables further graph optimization so it
executes the ownership-filtered graph under test.

`--cardinality-control` constructs two-key layers and requests two entirely
foreign keys. It reports that both the legacy and task-spec cull paths retain
all owned keys, directly demonstrating the false same-cardinality fast path.
It does not instrument which shortcut fires for each seed in the end-to-end
array graph; that correlation remains a future diagnostic.
