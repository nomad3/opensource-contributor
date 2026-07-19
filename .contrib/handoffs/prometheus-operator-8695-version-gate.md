# Handoff — Prometheus Operator PR #8695 version gate

## Objective

Prevent the operator from emitting `event_recorder` to Alertmanager versions
older than 0.33.0 while preserving the field at and above its introduction
boundary.

## Completed

- Built a minimal suggestion on top of PR commit `f127a0fc`.
- Added a repository-patterned warning and sanitizer drop below 0.33.0.
- Added boundary tests for 0.32.0 and 0.33.0 with load-bearing goldens.
- Created signed-off local commit `351e53a4`.
- Exported the commit as
  `.contrib/patches/prometheus-operator-8695-version-gate.patch`.
- Obtained an independent Claude Fable 5 adversarial review with verdict GO and
  no blocking or important findings.

## Evidence

```text
go test ./pkg/alertmanager -run 'TestSanitizeConfig|TestLoadConfig|TestEventRecorderConfig' -count=1
ok github.com/prometheus-operator/prometheus-operator/pkg/alertmanager

go test ./pkg/alertmanager -count=1
ok github.com/prometheus-operator/prometheus-operator/pkg/alertmanager

git diff --check
clean
```

## Next exact action

Post the prepared review on PR #8695 and offer the patch to its author. Do not
open a competing pull request.

## Remaining uncertainty

The parent pull request should still expand its field-mirror golden coverage;
that is independent from this narrowly validated version gate.

