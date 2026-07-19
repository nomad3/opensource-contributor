# Tekton Pipeline #4426 — debug script integration tests

- Issue: <https://github.com/tektoncd/pipeline/issues/4426>
- Upstream base: `7a2322246be0cbfa7255ac94cf426b051ba02a1c`
- Reconnaissance date: 2026-07-19
- Ownership: open, unassigned, no overlapping pull request
- Maintainer signal: reactivated and labeled `help wanted` on 2026-03-26

## Expected behavior

When a TaskRun reaches an on-failure or before-step breakpoint, the generated
scripts under `/tekton/debug/scripts` must release the paused entrypoint with
the requested outcome:

| Script | Expected TaskRun outcome |
| --- | --- |
| `debug-continue` | success |
| `debug-fail-continue` | failure |
| `debug-beforestep-continue` | execute the step, then success |
| `debug-beforestep-fail-continue` | skip the step and fail |

## Current coverage

Unit tests cover script generation, entrypoint arguments, wait-file behavior,
and breakpoint exit-code handling. No e2e test creates a real TaskRun, waits at
a breakpoint, executes a generated script inside the step container, and
observes the final TaskRun state.

## Smallest acceptable patch

Add one table-driven e2e test with four cases. Each case:

1. Requires `enable-api-fields=alpha`.
2. Creates an inline TaskRun with one named step and the relevant breakpoint.
3. Waits for the TaskRun and step container to be running.
4. Executes exactly one generated script through the Kubernetes exec API.
5. Asserts the final TaskRun success or failure state.

The helper should follow the existing e2e harness pattern for operations that
require `kubectl`, while passing arguments directly rather than invoking a
shell.

## Production impact

None. This is a test-only contribution and does not alter APIs, controllers,
generated files, or user-facing behavior.

## Risks

- Waiting only for TaskRun `Running` is insufficient; the step container must
  also be running before exec.
- A shared namespace would make parallel execution unsafe. The existing
  `setup()` helper provides an isolated namespace for each subtest.
- The feature is alpha, so the test must use the repository's feature-gate
  requirement helper.
- A local e2e run requires a cluster with the current Tekton build installed.

## Validation

```text
gofmt -w test/debug_scripts_test.go
go test -tags=e2e ./test -run '^$'
go test ./pkg/pod ./pkg/entrypoint
./hack/verify-agent-readiness.sh
```

With a disposable cluster containing the current source build:

```text
go test -v -count=1 -tags=e2e -timeout=20m ./test -run '^TestTaskRunDebugScripts$'
```
