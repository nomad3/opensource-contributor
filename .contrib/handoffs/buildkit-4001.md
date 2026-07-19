# Handoff

## Objective

Determine whether BuildKit issue #4001 is available and ready for a minimal,
maintainer-aligned OTLP documentation contribution.

## Completed

- Inspected current upstream `master` at `6dd0699`.
- Read contribution, DCO, documentation, and security-reporting conventions.
- Traced OTLP and legacy Jaeger detection from source.
- Inspected issue #4001, its timeline, and closed PR #6813 with `gh`.
- Confirmed the prior author's branch remains live.
- Captured the maintainer's requested documentation scope.
- Independently cross-reviewed the evidence with Fable 5 and Codex.

## Evidence

- Command: `go test ./util/tracing/detect/...`
- Result: PASS; Jaeger compatibility subpackage has no tests.
- Command: `gh pr view 6813 --repo moby/buildkit ...`
- Result: closed, not merged, changes requested; maintainer said "Reopen if you have updates."
- Command: GitHub API lookup of `dpk-jr/buildkit:docs/add-otlp-otlp-documentation`
- Result: branch remains present at `904bc73`.

## Current diff

No BuildKit file was modified. Only this control plane's dossier, tracker, and handoff
were updated.

## Next exact action

On or after 2026-08-01, re-check issue #4001, PR #6813, its source branch, assignees,
and related PR search. If still inactive, prepare a short, human-reviewed issue comment
asking whether taking over the maintainer-defined scope is welcome.

## Risks or unanswered questions

- The prior author may still intend to address the requested changes.
- Docker's separate documentation repository may require a coordinated follow-up.
- An end-to-end Collector example must be tested before it is proposed.

## Do not do

- Do not open a competing PR while ownership is unresolved.
- Do not copy PR #6813's overbroad protocol documentation.
- Do not remove runtime support for legacy Jaeger variables.
- Do not post externally without human approval.
