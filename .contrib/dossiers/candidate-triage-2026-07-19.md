# Candidate triage — 2026-07-19

## Objective

Select the next profile-aligned contribution without duplicating active work or
claiming an issue whose behavior is not agreed.

## Findings

| Project | Issue | Evidence | Decision |
| --- | --- | --- | --- |
| scikit-learn | [#28793](https://github.com/scikit-learn/scikit-learn/issues/28793) | Reserved for sprint participants; stalled PR #30307 exists. | Wait. |
| OpenTelemetry Python Contrib | [#476](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/476) | Client support is merged. The server-side author's draft PR #3928 was closed only by the inactivity bot and can be reopened. | Wait or ask before takeover. |
| Kueue | [#1473](https://github.com/kubernetes-sigs/kueue/issues/1473) | Active PR #13069 overlaps the requested `SECURITY-INSIGHTS` scope. | Wait. |
| Kueue | [#9402](https://github.com/kubernetes-sigs/kueue/issues/9402) | Maintainers and users have not resolved whether configuration is global or cohort-level. | Blocked on design. |
| Moby | [#50732](https://github.com/moby/moby/issues/50732) | Active PR #52714 adds the proposed fail-fast and rerun-report behavior. | Wait. |

## OpenTelemetry implementation evidence

PR #3928 proposed a four-line server interceptor change using
`is_instrumentation_enabled()`. It contains no regression test or changelog and
received no maintainer review before automatic closure. Reimplementing it now
would silently take over another contributor's stated work. The appropriate
next action is to request coordination if the issue becomes the preferred task,
not to publish a duplicate patch.

## Selection rule

Continue discovery in the existing profile-aligned queue. A task becomes active
only when all of the following are true:

1. The issue is open, unassigned, and not reserved.
2. No active or reasonably resumable pull request overlaps it.
3. Expected behavior is supported by maintainer guidance or current tests.
4. A bounded first artifact can be produced without an external post.
