# Maintainer review: OpenCost PR #3917

- Pull request: <https://github.com/opencost/opencost/pull/3917>
- Issue: <https://github.com/opencost/opencost/issues/3916>
- Reviewed head: `10b8665b233fcd90a2aeab66632594af72ec17bd`
- Review date: 2026-07-19
- Mode: read-only; no upstream comment, review, commit, or branch mutation
- Verdict: **DO NOT PROMOTE YET**

## Scope and intent

The pull request adds an early semantic guard to `CostDataModel`:

```go
if timeutil.DurationString(duration) == "" {
    WriteData(w, nil, fmt.Errorf("illegal window: %s", window))
    return
}
```

It also adds a table-driven regression test for malformed, missing, zero,
negative, and sub-second windows. This is a narrow response to issue #3916:
keep `0m`, `-1h`, and `1ms` from reaching the Prometheus-backed model path.

## Findings

### BLOCKING

1. **The substantive repository gates did not execute.**

   At the reviewed head, the `Build/Test`, `Format Check`, and `Generate SBOM`
   workflow runs all concluded `action_required` and each exposed zero jobs:

   | Workflow | Run | Jobs |
   | --- | --- | ---: |
   | Build/Test | [29564721658](https://github.com/opencost/opencost/actions/runs/29564721658) | 0 |
   | Format Check | [29564721760](https://github.com/opencost/opencost/actions/runs/29564721760) | 0 |
   | Generate SBOM | [29564721688](https://github.com/opencost/opencost/actions/runs/29564721688) | 0 |

   The integration workflow's visible success is not substitute evidence: its
   build, test, comparison, data-collection, and teardown jobs were skipped;
   only permission/no-op/control jobs passed. DCO and SonarQube are green, but
   they do not establish that the Go package builds, its tests pass, or the
   repository remains formatted. Promotion should wait for an authorized
   maintainer CI run or equivalent reproducible evidence on the current head.

### IMPORTANT

1. **The branch is behind `develop`.**

   GitHub reports `mergeStateStatus: BEHIND`. Rebase or merge the current base,
   then run the substantive gates against the resulting head before approval.

2. **The endpoint still maps invalid client input to HTTP 500.**

   The new test deliberately asserts `StatusInternalServerError`. This
   preserves existing `WriteData` behavior and is defensible for this narrow
   panic-prevention patch, but it means the API still reports a server failure
   for malformed client input. A separate issue should decide whether the
   contract should become HTTP 400; that behavior change should not be slipped
   into this patch without maintainer agreement.

3. **Fractional durations above one second remain accepted and truncated.**

   `DurationString` converts `duration.Seconds()` to `int64`, so values such as
   `1100ms` or `1.1s` become `1s`. The author explicitly scoped this pull
   request to inputs that produce an empty Prometheus duration string. That is
   consistent with the reported reproducer, but exact whole-second validation
   remains an acknowledged follow-up rather than a solved part of the broader
   input-validation problem.

### OPTIONAL

1. Assert the response error text in the regression test. The nil model makes
   reaching `ComputeCostData` fail loudly and therefore proves the early return
   indirectly, but checking the `"illegal window"` response would document the
   intended rejection path more explicitly.

## Logic assessment

The four-line production change is appropriately small and follows an existing
conversion boundary used by downstream Prometheus query construction.
`DurationString` returns an empty string for non-positive and sub-second
durations, so the guard covers the issue's three semantic reproducers before
`ComputeCostData` is invoked. The malformed and missing cases continue to exit
through `ParseDuration`.

The request helper now uses `URL.Query` and `Encode`, avoiding hand-built query
strings. The final formatting-only changes are mechanical `gofmt` alignment in
the same test file and do not introduce behavior.

## Evidence inspected

- Issue #3916 description and reproducer matrix
- Complete PR patch and commit sequence
- `CostDataModel` at the reviewed head
- `timeutil.DurationString` implementation
- Inline review discussion and author scope decisions
- PR comments, review state, merge state, and check summary
- GitHub Actions run metadata and job counts
- SonarQube report: quality gate passed, 100% coverage on new code
- DCO: passed
- Snyk: error attributed to the external account's private-test quota, not a
  reported vulnerability result

## Promotion boundary

Re-evaluate when the branch is current and `Build/Test`, `Format Check`, and
`Generate SBOM` have actually executed successfully on that head. The narrow
code change does not presently require redesign; the blocker is missing
integration evidence. Do not post this review upstream without human
verification.
