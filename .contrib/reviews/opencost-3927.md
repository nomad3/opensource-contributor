# Maintainer review: OpenCost PR #3927

## Verdict

**DO NOT PROMOTE YET.**

The nil-response fix and regression-test logic are correct at source-review
level. Promotion is blocked by an unrelated third commit and the absence of
executed Build/Test, Format Check, and SBOM workflows on the current head.

This is a private review artifact. No GitHub review, issue comment, or pull
request comment was posted.

## Pull request state

- PR: [opencost/opencost#3927](https://github.com/opencost/opencost/pull/3927)
- Issue: [#3926](https://github.com/opencost/opencost/issues/3926)
- Base: `develop`
- Head: `73a4e89c86a3a5eb5772e5c7dc17b1ba93e025da`
- Refreshed: 2026-07-19T03:38:10Z
- State: open, non-draft, review required
- Mergeability: mergeable
- Branch relation: 3 commits ahead and 5 commits behind `develop`
- Human maintainer approvals: none

## What the patch does

The production change makes both shared rate-limit helpers total for a nil
HTTP response:

```go
if resp == nil {
    return false
}
```

The test mock now supports a per-call error. The regression sequence is:

1. initial response is HTTP 429;
2. the retry returns `(nil, nil, errTransportFailed)`;
3. rate-limit evaluation returns false rather than panicking; and
4. `errors.Is()` proves the original transport error reaches the caller.

## Correctness assessment

The change fixes the reported failure:

- `RateLimitedPrometheusClient.worker()` enters retry only after a non-nil
  initial response.
- After a transport error, the loop condition calls
  `httputil.IsRateLimited(nil, nil)`.
- `IsRateLimited()` calls both helpers; the new guards make each return false.
- The retry loop exits with the transport error still in `err`.
- The test asserts error identity, so it cannot pass on an unrelated
  retries-exhausted error.

Guarding the shared helpers is preferable to guarding only the caller because
their exported signatures accept pointers and nil means “no rate-limit
response.” The zero-value `Error` field leaves all existing mock cases
unchanged.

The empty URL in `http.NewRequest(http.MethodPost, "", nil)` is valid in Go and
matches existing tests. The automated comment objecting to it is not a defect.

## BLOCKING

### 1. Remove the unrelated router formatting commit

Current head adds:

```text
73a4e89 style: format router_test.go
```

It changes only alignment in `pkg/costmodel/router_test.go` and is unrelated to
Prometheus retry behavior. Earlier automated review covered the original two
files, not this third-file head. The PR should contain one logical fix and its
test; drop this commit/change before merge.

### 2. Execute the substantive checks on the final head

For head `73a4e89`:

| Workflow | Conclusion | Jobs |
| --- | --- | ---: |
| Build/Test | `action_required` | 0 |
| Format Check | `action_required` | 0 |
| Generate SBOM | `action_required` | 0 |

The pull-request-target integration workflow is green only because it ran
permission/no-op jobs. Image build, stack setup, integration tests, comparison
tests, and teardown were skipped. This does not validate the code.

Snyk also reports an error state. SonarQube reports a passing quality gate but
`0.0%` new-code coverage, so it does not replace the missing Go tests.

The PR description claims:

```text
go test ./pkg/prom/...
go test ./pkg/util/httputil/...
```

Those paths are stale for the current repository layout. The packages live
under `modules/prometheus-source/pkg/prom` and `core/pkg/util/httputil`.
Whether the author ran correct commands locally is therefore not independently
established by the description.

Before promotion, run or authorize on the cleaned final head:

```bash
go fmt ./...
git diff --check
go vet ./...
go test ./core/pkg/util/httputil/... -count=1
go test ./modules/prometheus-source/pkg/prom/... -count=1
just test
```

If fork workflows require maintainer authorization, the appropriate maintainer
should authorize them after the unrelated commit is removed.

## IMPORTANT

### Keep the transport-error assertion

The original automated review correctly requested a sentinel error and
`errors.Is()`. The current head contains that improvement. It must remain
through any rebase or cleanup.

### Rebase or update against current `develop`

The branch is five commits behind `develop`. Recheck the diff and rerun all
required checks after updating, because current mergeability alone does not
prove the tested head matches the eventual merge result.

## OPTIONAL

- Add direct table cases for
  `IsRateLimitedResponse(nil)` and `IsRateLimitedBody(nil, body)` in
  `core/pkg/util/httputil/httputil_test.go`. The end-to-end regression already
  invokes both guards, so these are clarity tests rather than a correctness
  blocker.
- Rename the test comment to describe expected behavior rather than repeating
  the test name.

## Scope and compatibility

- No API signature changes.
- No retry-count or backoff behavior changes.
- Non-nil rate-limit responses retain existing behavior.
- Transport errors after a rate-limited response are returned instead of
  crashing a worker.
- No dependency changes.

## Promotion checklist

- [ ] Remove `pkg/costmodel/router_test.go` from the PR.
- [ ] Update the branch against current `develop`.
- [ ] Preserve the sentinel transport-error assertion.
- [ ] Run Build/Test and Format Check with real jobs.
- [ ] Run the focused util and Prometheus-source tests.
- [ ] Run the repository-wide `just test` gate or obtain equivalent trusted CI.
- [ ] Resolve or explain the Snyk error.
- [ ] Obtain human maintainer review.
