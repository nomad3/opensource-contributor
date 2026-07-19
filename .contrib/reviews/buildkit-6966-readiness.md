# BuildKit PR #6966 readiness review

- Pull request: <https://github.com/moby/buildkit/pull/6966>
- Title: `detect: read OTEL_IGNORE_ERROR from environment`
- Status checked: 2026-07-19
- PR head: `14e0dfbd2cdcae3f1f29d9560bd90341cba55eb0`
- PR base: `6dd06999d5d369a217c3f3259a420f507e2db2c7`
- Current upstream `master`: `6dd06999d5d369a217c3f3259a420f507e2db2c7`
- Mode: read-only; no upstream state or comment changed
- Verdict: **PATCH READY; UPSTREAM CI APPROVAL REQUIRED**

## Current state

The draft pull request is open, mergeable, and contains one signed-off commit.
Its scope remains:

- one production-line correction in `util/tracing/detect/detect.go`;
- one 43-line table-driven regression test in
  `util/tracing/detect/detect_test.go`;
- no dependency, documentation, generated-file, or unrelated formatting change.

There are no comments or reviews. DCO, label assignment, and author assignment
passed. The head SHA has not changed since publication.

## Why only three checks appear on the pull request

The substantive workflows were created for the PR head but immediately
completed with conclusion `action_required`:

| Workflow | Run | Conclusion |
|---|---:|---|
| validate | `29669477183` | `action_required` |
| compatibility-releases | `29669477214` | `action_required` |
| test-os | `29669477219` | `action_required` |
| buildkit | `29669477347` | `action_required` |
| frontend | `29669477394` | `action_required` |
| zizmor | `29669477412` | `action_required` |

The labeler and author-assignment workflows use `pull_request_target`, so they
ran successfully without executing fork-controlled code. DCO also passed.

This is not a test failure and not evidence that workflow path filters excluded
the patch. BuildKit's `buildkit.yml`, `validate.yml`, `test-os.yml`, and
`frontend.yml` all subscribe to `pull_request`; the changed Go files are not in
their ignored documentation paths. The runs completed with `action_required`
and require a repository maintainer's approval before their jobs can execute
fork-controlled code.

## Freshness check

At review time, upstream `master` still equals the PR base:

```text
6dd06999d5d369a217c3f3259a420f507e2db2c7
```

Therefore:

- the branch is not behind;
- neither detector source nor module metadata changed after local validation;
- no rebase or retest is required solely for upstream drift.

The existing focused evidence remains applicable:

```text
go test ./util/tracing/detect/... -run TestDetectExporterIgnoreErrors -v  PASS
go test ./util/tracing/detect/...                                    PASS
go vet ./util/tracing/detect/...                                     PASS
gofmt -l util/tracing/detect/                                        no output
```

The test was also independently shown to fail for the expected unsupported
exporter error before the production line was corrected.

## Maintainer-style patch review

### Correctness

The change restores the exact environment lookup that existed before refactor
commit `228e250d`. Parsing the literal string `"OTEL_IGNORE_ERROR"` cannot
succeed; parsing `os.Getenv("OTEL_IGNORE_ERROR")` restores the intended
`strconv.ParseBool` behavior.

### Test quality

- The default-error case prevents accidental unconditional suppression.
- The enabled case covers both trace and metric public constructors.
- An unknown exporter fails before detector execution, so the test makes no
  network request and does not mutate the package-global detector registry.
- `t.Setenv` restores state and prevents unsafe parallel execution.
- Nil exporter assertions cover the return value as well as the error.

### Scope and compatibility

The patch changes only a previously supported opt-in behavior. Operators already
setting a true `OTEL_IGNORE_ERROR` value regain suppression of exporter
detection errors. Invalid or absent values retain the default error behavior.

No blocking or important code concern was found in this readiness refresh.

## Exact upstream action boundary

The patch is technically ready, but full upstream evidence does not exist until
a BuildKit maintainer selects **Approve and run workflows** for the fork runs.
The contributor cannot bypass this repository gate.

Recommended sequence:

1. With explicit human authorization, convert the PR from draft to ready for
   review; do not add a comment merely to attract attention.
2. Wait for a maintainer to approve the pending fork workflows.
3. Require all applicable substantive checks to complete successfully.
4. If a check fails, diagnose only that failure and keep the two-file scope.
5. Respond narrowly to human review; do not combine the separate OTLP
   documentation work.

Do not push a no-op commit, close/reopen the PR, or attempt to rerun the
`action_required` workflows. Those actions do not replace maintainer approval
and would add noise.

## Promotion decision

The next state-changing action is converting #6966 from draft to ready for
review. That is appropriate now from a code-readiness perspective, but it should
remain a deliberate human-authorized upstream action. Until then, keep BuildKit
#6966 as the sole active implementation and continue read-only monitoring.
