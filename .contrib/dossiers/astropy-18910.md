# Astropy #18910 — one-table stacks return the input despite a new-table contract

## Identity

- Repository: `astropy/astropy`
- Issue:
  [#18910](https://github.com/astropy/astropy/issues/18910)
- Issue state: open, labeled `table` and `Bug`, unassigned, with no linked
  development
- Current `main` commit inspected:
  [`7893da4`](https://github.com/astropy/astropy/commit/7893da4359a15ab053105c6c0fe9b18f3b81b12b)
- Current release inspected: `v8.0.1` at
  [`7c5a9c1`](https://github.com/astropy/astropy/commit/7c5a9c124ce84c76992016e89631566ad398aff7)
- Live ownership, overlap, source, history, and policy check:
  `2026-07-19T06:40:44Z`

## Decision boundary

The defect is source-confirmed, astronomy-native, and small enough for an
offline regression. The implementation contract is not settled.

For an actual `Table` or `QTable`, a one-input `vstack()`, `hstack()`, or
`dstack()` returns the exact input object. Each function documents its result
as a new table. Through this exact-identity path, downstream mutation can
therefore change the caller's original table when the input cardinality happens
to be one. The issue directly demonstrates that replacing result metadata also
replaces the input table's metadata.

Changing that behavior is not automatically a safe one-line fix. Maintainers
must decide:

1. whether the documented new-object promise or the historical identity fast
   path is authoritative;
2. whether a new result must isolate only the table container, its column data,
   nested table and column metadata, indices, and mixins;
3. whether the issue covers only `vstack()` or all three functions with the
   same shortcut;
4. whether a code change is main-only and older release lines receive, at
   most, a documentation clarification;
5. whether singleton `dstack()` preserves each column's historical cell shape
   or follows the documented depth-stack model and inserts a one-layer depth
   axis.

Copying a large one-table catalog also replaces an effectively constant-time
path with work proportional to the selected copy depth.

Decision: **GO for this source-only dossier; WAIT for implementation, runtime
work, and upstream contact.** BuildKit PR #6966 remains this portfolio's sole
active implementation.

## Scientific and data-pipeline impact

Astronomy workflows often normalize zero, one, or many observation, catalog,
or event-table fragments through the same stack operation. With the current
shortcut, otherwise identical post-stack cleanup has cardinality-dependent
ownership:

- a one-fragment result is the cached or caller-owned input;
- a multi-fragment result is a separately constructed table, although this
  audit did not prove isolation for every nested buffer, mixin, or metadata
  object.

The verified singleton alias and metadata effect make cardinality-dependent
catalog or provenance mutation plausible: a pipeline may depend on query result
count, partitioning, or filtering rather than its explicit data contract.

That pipeline impact is an inference, not a verified catalog incident or
evidence that a published scientific result has been corrupted. No real-world
incidence was measured.

## Pinned behavior matrix

The relevant current source is
[`astropy/table/operations.py`](https://github.com/astropy/astropy/blob/7893da4359a15ab053105c6c0fe9b18f3b81b12b/astropy/table/operations.py).
The corresponding
[`v8.0.1` source](https://github.com/astropy/astropy/blob/7c5a9c124ce84c76992016e89631566ad398aff7/astropy/table/operations.py)
has the same relevant behavior.

| Version | Operation | Documented return | One-table path | Existing focused assertion |
| --- | --- | --- | --- | --- |
| current `main` | `vstack()` | New table containing stacked data | `return tables[0]` | Value equality only |
| current `main` | `hstack()` | New table containing stacked data | `return tables[0]` | Value equality only |
| current `main` | `dstack()` | New table containing stacked data | `return tables[0]` | Direct `Table` value equality only |
| `v8.0.1` | `vstack()` | New table containing stacked data | `return tables[0]` | Value equality only |
| `v8.0.1` | `hstack()` | New table containing stacked data | `return tables[0]` | Value equality only |
| `v8.0.1` | `dstack()` | New table containing stacked data | `return tables[0]` | Direct `Table` value equality only |

This matrix is a pinned source and test audit. The behavior was not executed
locally.

## Input-normalization boundary

All three functions first call `_get_list_of_tables()`:

- a non-sequence input is wrapped in a new list;
- an input sequence is copied to a new list, so element conversion does not
  replace entries in the caller's container;
- `Table` and `QTable` elements pass through unchanged;
- `Row`, `Quantity`, and other column-like values are converted into a table.

The alias therefore applies directly to both `stack(table)` and
`stack([table])` when the value is a `Table`, `QTable`, or subclass. A `Row`,
`Quantity`, or other accepted non-table input crosses a conversion boundary
before the shortcut and does not prove the same object-identity defect.

This distinction matters for a future parameterized test. Treating every
accepted input as an equivalent alias case would overstate the bug and could
freeze unrelated conversion behavior.

Public `vstack()` and `hstack()` are not the only identity fast paths.
Their private `_vstack()` and `_hstack()` helpers also return the sole input
array. The public early returns make those private singleton paths unreachable
through ordinary calls today, but simply deleting the public shortcuts and
delegating would not establish a new-result contract.

## `dstack()` rank and index boundary

The public `dstack()` shortcut runs before its ordinary `vstack()` plus
reshape-and-transpose path. For an ordinary one-dimensional column, a singleton
table therefore retains shape `(n,)`. More generally, a column retains
`(n, *cell_shape)`. The
[table operations guide](https://github.com/astropy/astropy/blob/7893da4359a15ab053105c6c0fe9b18f3b81b12b/docs/table/operations.rst)
describes depth stacking in NumPy-like terms, and the multi-input path produces
columns accessed through a depth dimension.

This creates a separate contract decision:

- returning `tables[0].copy()` can remove object aliasing while preserving
  `(n, *cell_shape)`, including `(n,)` for a scalar-valued column;
- using a safe ordinary depth-stack path can produce
  `(n, 1, *cell_shape)`, including `(n, 1)` for a scalar-valued column, and
  make singleton rank consistent with depth stacking.

The second choice also affects indices because Astropy table indices cannot be
attached to multi-dimensional columns. This is not just a choice between
identity and copying; `dstack()` needs an explicit rank and index contract.

Deleting only `dstack()`'s public singleton guard is unsafe. Its ordinary path
calls the current public `vstack([table])`, which still returns the input
object; the following private column reshape and replacement would then mutate
the caller's table. A depth-axis solution must first create an independent
result or change the `vstack()` singleton contract simultaneously.

## Historical intent

[PR #3313](https://github.com/astropy/astropy/pull/3313), merged in 2015 as
[`5b513f7`](https://github.com/astropy/astropy/commit/5b513f7636cd7bc9925bc12f353d8ceb628dd28c),
fixed failures when `vstack()` or `hstack()` received a single table. It
explicitly sought to return that table, introduced the direct `tables[0]`
returns, and added regression tests that compare values. Those tests did not
assert object identity, mutation isolation, or a copy-depth contract. The
change did not cover `dstack()`.

That history makes the shortcut intentional rather than an accidental recent
regression. It does not reconcile the shortcut with the current return
documentation.

[PR #16130](https://github.com/astropy/astropy/pull/16130), merged in 2024 as
[`47a8dac`](https://github.com/astropy/astropy/commit/47a8dac8f1dab6ce592be6048f70140adead4e1d),
later prevented `_get_list_of_tables()` from replacing elements in the caller's
input list while converting a `Row`. Its regression preserves the identities
of the original list elements. It is useful evidence that stack operations
should avoid surprising mutation of caller-owned inputs, but it does **not**
define output identity, buffer ownership, metadata isolation, or copy depth.

## Issue discussion and unresolved contract

The issue demonstrates `vstack([input_table]) is input_table` and shows that
replacing result metadata also changes the input. Discussion has considered
both legitimate resolutions:

- document the one-table identity exception; or
- make the implementation honor the new-table return description.

All three participants are repository members, but no accepted or authoritative
table-maintainer resolution exists. Their positions at the live check were:

- `pllim` initially preferred documentation, then considered copying
  reasonable but breaking, with no behavioral backport and a possible
  stable-documentation clarification;
- `eerovaher` favored eliminating the special case so code matches the return
  documentation and characterized the silent alias as dangerous;
- reporter `mwcraig` preferred an always-new result but explicitly deferred to
  table maintainers because callers may rely on identity.

These are discussion positions, not an accepted project decision. Copy depth,
three-operation scope, `dstack()` rank, and release-line treatment remain
unresolved.

The source shows the same shortcut in `hstack()` and `dstack()`. That adjacent
evidence is sufficient to include them in contract analysis, not to assume
that maintainers want one issue to change all three APIs.

## Existing tests and missing coverage

Pinned current tests:
[`astropy/table/tests/test_operations.py`](https://github.com/astropy/astropy/blob/7893da4359a15ab053105c6c0fe9b18f3b81b12b/astropy/table/tests/test_operations.py).

The `operation_table_type` fixture exercises both `Table` and `QTable`.
`TestVStack.test_vstack_one_table` and
`TestHStack.test_hstack_one_table` cover direct and one-element-list inputs,
but only compare table values. They pass whether the result aliases the input
or is independently copied. `TestDStack.test_dstack_single_table` covers only
direct `dstack(table)` with an ordinary `Table` and likewise asserts value
equality only. It does not cover `QTable`, the one-element-list form, identity,
isolation, or the singleton depth shape.

Existing multi-table tests cover metadata merging, masking, quantities, and
representative mixins. They do not establish the desired semantics of the
one-table shortcut. In ordinary multi-table paths, result construction and
metadata merging already take different ownership paths, so those tests are
not a substitute for the singleton contract.

Missing focused coverage includes:

- `out is input`;
- top-level and nested table metadata isolation;
- column data and column-info metadata isolation;
- index preservation and independence;
- representative mixin behavior;
- consistency among `vstack()`, `hstack()`, and `dstack()`;
- the distinction between actual tables and inputs converted into tables.

## Smallest future offline regression design

No network, external catalog, observatory data, GPU, or HPC environment is
required. After maintainers select the contract, extend the existing one-table
tests with a small parameterized matrix:

| Dimension | Cases |
| --- | --- |
| Operation | `vstack`, `hstack`, `dstack` if the approved scope includes each |
| Invocation | `operation(table)`, `operation([table])` |
| Table type | `Table`, `QTable` |
| Fixture | composite `Table` with an indexed plain column and nested table/column metadata; composite `QTable` with a `Quantity` and one representative mixin |

For a new-result contract, first assert:

```python
out is not input_table
```

Then preserve the exact result class, values, column classes, units, metadata,
and the outer input list before probing the approved isolation depth. Candidate
mutation probes are:

1. replace `out.meta`;
2. mutate a nested object within `out.meta`;
3. change one output cell or column value;
4. change output column metadata;
5. mutate or remove an output index where the selected operation contract
   preserves one;
6. change representative quantity or mixin-backed data.

Do not commit all six as independence requirements until maintainers decide
whether the result is a container copy, a data copy, or a deeper semantic copy.
The first metadata-replacement probe directly captures the issue report; the
others distinguish contracts that currently remain unresolved.

If maintainers instead choose to document the alias, add an explicit identity
assertion and a prominent API note so callers do not infer isolation from “new
table.” That would preserve the performance fast path but make the
cardinality-dependent ownership contract intentional.

The initial focused nodes should remain the existing one-table tests:

```text
astropy/table/tests/test_operations.py::TestVStack::test_vstack_one_table
astropy/table/tests/test_operations.py::TestHStack::test_hstack_one_table
astropy/table/tests/test_operations.py::TestDStack::test_dstack_single_table
```

Parameterize or extend the third node only if the accepted scope includes
`dstack()`, and assert its selected `(n, *cell_shape)` or
`(n, 1, *cell_shape)` result shape, including the scalar-valued `(n,)` versus
`(n, 1)` case. Then run the table operations test module and `tox -e test`;
focused nodes and the module are diagnostics, not substitutes for the project
test gate and CI. These commands are a future validation design; none ran in
this cycle.

## Compatibility, performance, and rollback risks

### Copy depth

A fresh `Table` object can still share column buffers, nested metadata, mixin
state, or indices with its source. A patch that merely changes object identity
could satisfy the issue's first assertion while leaving mutation channels that
users reasonably interpret as violating a new-table promise.

Pinned current
[`Table.copy(copy_data=True)`](https://github.com/astropy/astropy/blob/7893da4359a15ab053105c6c0fe9b18f3b81b12b/astropy/table/table.py#L3808-L3825)
is a concrete strong candidate: it preserves the exact table class, copies
underlying data, deep-copies table metadata, recreates groups, and
[clones indices](https://github.com/astropy/astropy/blob/7893da4359a15ab053105c6c0fe9b18f3b81b12b/astropy/table/tests/test_index.py#L481-L513)
onto copied columns. That does not settle stack semantics. Normal multi-input
[`hstack()` explicitly drops indices](https://github.com/astropy/astropy/blob/7893da4359a15ab053105c6c0fe9b18f3b81b12b/astropy/table/tests/test_index.py#L650-L658),
so preserving cloned indices in the singleton path versus dropping them for
stack parity is a maintainer decision. A depth-stacked
`(n, 1, *cell_shape)` result cannot retain ordinary indices on its
multi-dimensional columns.

Conversely, deep-copying every nested or mixin object may be expensive,
unsupported for some user objects, or stronger than other Astropy table
operations promise. The patch should name and test the intended boundary.

### Historical compatibility

Code may rely on the singleton result being the same object, even if that
behavior conflicts with the documentation. The 2015 regression and long-lived
fast path increase that risk. A release note and an explicit maintainer
decision are required for a behavior change.

### Performance and memory

The current shortcut performs no table-data copy. A full data copy makes the
one-input case proportional to catalog size and temporarily requires
additional memory. Benchmarks are unnecessary for the tiny regression, but
the chosen contract should state whether large columns are copied and why.

### Three-operation consistency

Fixing only `vstack()` would leave two functions with the same documented
new-table wording and shortcut. Changing all three without maintainer agreement
would broaden a narrowly reported issue. Preserve this as an explicit API
decision rather than hiding it in implementation.

### Release lines

The inspected discussion proposes changing current code without behavior
backports and possibly clarifying stable documentation. That is a participant's
proposal, not accepted policy. Project pull requests target `main`; active
backport labels include `backport-v8.0.x` and `backport-v7.2.x`, and the manual
backport template requires `skip-basebranch-check` before opening. Maintainers
must decide whether this issue receives a main-only behavior change, a
documentation backport, neither, or another treatment.

## Ownership and overlap

At the live check:

- the issue was unassigned;
- its timeline contained labels and comments but no linked development;
- an exact `18910` pull-request search returned no result;
- target-repository refs `heads/18910` and `heads/vstack` did not exist;
- focused title and phrase searches returned only closed pull requests;
- closed PR
  [#19280](https://github.com/astropy/astropy/pull/19280) is unmerged and
  labeled `invalid`; its surviving fork branch changes FITS 999-column
  guarding, not table operations, so it is an unrelated search false positive.

These bounded searches did not find overlap; they cannot prove that no
implementation exists anywhere.

Recheck assignment, comments, linked development, matching pull requests, and
branches immediately before any future upstream contact or implementation.

## Contribution and AI policy

Astropy's
[contribution guide](https://github.com/astropy/astropy/blob/7893da4359a15ab053105c6c0fe9b18f3b81b12b/CONTRIBUTING.md)
targets contributions at `main` and requires appropriate tests, documentation
for functionality, and a changelog for user-visible changes. A future table bug
fix uses `docs/changes/table/<PR>.bugfix.rst`. The project gate is
`tox -e test` plus CI; focused nodes and the operations module are diagnostic
steps, not a stated replacement. The pinned project floors are Python 3.11 and
NumPy 2.0.

The Astropy Project's pinned
[AI-assisted contribution policy](https://github.com/astropy/astropy-project/blob/b842b9bef3c8d69da73d639ea0254ae17fbc1fd1/policies/ai-policy.md)
permits AI assistance while making the human contributor responsible for
correctness, licensing, explaining the change, following project style, and
engaging reviewers directly. No mandatory AI-disclosure, DCO, or CLA rule was
found in the inspected authoritative files; the repository also reports
`web_commit_signoff_required=false`. This is a bounded policy search, not proof
of universal absence. Revalidate those policies before contributing.

## Execution and resource boundary

This cycle used public issue, source, history, test, and policy inspection
only. It created:

- no Astropy checkout or worktree;
- no Python environment or dependency download;
- no test data, runtime reproduction, benchmark, or generated file;
- no branch, patch, comment, pull request, review, or other upstream mutation.

A future focused regression is CPU-, memory-, and storage-light. The full
Astropy test environment is materially larger. Local storage was 96% used with
about 16.9 GiB available during the final audit, so no checkout or dependency
work should begin without a fresh capacity check and cleanup plan.

## Decision

- Status: **waiting**
- Evidence verdict: **GO**
- Dispatch verdict: **WAIT**
- Blockers:
  - maintainers have not chosen documentation versus a new result object;
  - copy depth is undefined;
  - one-operation versus three-operation scope is undefined;
  - singleton `dstack()` rank and index behavior is undefined;
  - code and documentation backport policy is undefined;
  - BuildKit PR #6966 occupies the sole implementation slot.
- Next exact action: preserve this dossier, monitor issue #18910, and after the
  implementation slot clears and contact is authorized, revalidate ownership
  and ask maintainers to select the object, copy depth, operation scope,
  `dstack()` rank/index, and release contract before writing the focused
  regression.
- Resumable stopping point: pinned main and `v8.0.1` matrix, historical intent,
  no-input-mutation precedent, and an unexecuted offline regression design are
  documented; no implementation semantics were selected.
