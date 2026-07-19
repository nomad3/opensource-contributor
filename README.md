# Open Source Contribution Control Plane

A public, evidence-first system for turning spare AI-assisted engineering capacity into
small, reviewable contributions to critical open-source infrastructure.

The portfolio is maintained by [Simon Aguilera](https://github.com/nomad3), a senior
SRE, DevSecOps, cloud, and AI platform engineer. The focus is the intersection of:

- Kubernetes and production AI platforms
- Reliability, observability, and incident response
- CI/CD and software supply-chain security
- MLOps, model serving, and distributed systems
- FinOps and cloud cost governance

## Operating principles

1. Professional work keeps priority.
2. One upstream implementation is active at a time.
3. Reconnaissance precedes code.
4. A regression test should fail for the expected reason before production code changes.
5. Patches stay minimal and avoid unrelated refactoring or dependency updates.
6. A second review pass challenges behavior, compatibility, security, and operational risk.
7. Agents prepare external communication; a human verifies and posts it.
8. Blocked, assigned, or overlapping work returns to the waiting queue.
9. Every session leaves a persistent artifact: evidence, a test, a patch, a review, or a handoff.

## Capacity model

| Available capacity | Work unit | Durable output |
| --- | --- | --- |
| Under 10% | Inspection | Reproduction command, issue note, file map, or review |
| 10-25% | Micro-task | Test fixture, documentation, assertion, or minimal reproducer |
| 25-50% | Small patch | Failing regression test and minimal fix |
| Over 50% | Deep task | Benchmark, CI investigation, controller analysis, or bounded feature |

Usage percentages are decision aids, not token accounting. Provider usage meters and
reset information remain the source of truth.

## Repository map

- [Portfolio](portfolio.md) ranks projects against the maintainer's background.
- [Tracker](.contrib/tracker.yaml) contains the active, ready, and waiting queues.
- [Inbox](.contrib/inbox.md) captures opportunities without starting investigation.
- [Dossier template](.contrib/dossiers/TEMPLATE.md) defines reconnaissance evidence.
- [Handoff template](.contrib/handoffs/TEMPLATE.md) preserves resumable state.
- [Agent prompts](.contrib/prompts/) separate investigation, implementation, and review.
- [Observer prompt](.contrib/prompts/observer.md) coordinates candidate research,
  enforces ownership gates, and protects the one-active-implementation rule.
- [Observer Manager skill](skills/observer-manager/SKILL.md) provides a reusable,
  installable supervisor for capacity, queues, CI/reviews, handoffs, and cleanup.
- [Observer state](.contrib/observer-manager.yaml) records the current decision
  without granting the agent authority to communicate upstream.
- [Contributing](CONTRIBUTING.md) explains how to suggest or validate an opportunity.

## Current direction

The initial sequence is:

1. BuildKit telemetry documentation and reproducibility
2. Moby CI and flaky-test evidence
3. Kueue or OpenTelemetry observability specialization
4. KServe work when a non-overlapping issue is available

Project and issue state changes quickly. Entries are revalidated immediately before
implementation.

## Safety and attribution

No employer code, confidential operational data, credentials, CV files, or private
incident information belongs here. AI assistance may be used for investigation,
implementation, and review, but every submitted change must be understood, tested, and
consistent with the upstream project's contribution and AI-use policies.
