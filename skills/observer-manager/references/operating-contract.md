# Observer-manager operating contract

## Authority boundary

The observer may read local and public upstream state, rank work, request
evidence, dispatch bounded agents, update repository-local control-plane
artifacts when authorized, and stop unsafe or duplicate work.

The observer does not implement upstream code, speak for the contributor,
claim issues, submit reviews, or change external state by default. A worker's
confidence never replaces maintainer guidance or test evidence.

## Capacity routing

| Remaining usable capacity | Work unit | Required persistent output |
| --- | --- | --- |
| Under 10% | Inspection | issue note, reproduction command, file map, or review |
| 10–25% | Micro-task | reproducer, failing test, docs patch, or CI diagnosis |
| 25–50% | Small patch | confirmed regression test plus minimal fix |
| Over 50%, reset near | Deep task | architecture map, benchmark, or bounded implementation |

When weekly reset is distant, preserve capacity even if a session meter is
high. Usage meters and reset timestamps are the source of truth. If no meter is
available, record capacity as unknown and limit dispatch to observation.

## GitHub CI inspection

Do not rely only on pull-request `statusCheckRollup`. Query workflow runs for
the exact head commit and record zero-job runs, `action_required`, skipped, and
cancelled conclusions. Use `authorization-required` for verified
`action_required` state; describe fork approval or maintainer authorization as
an inference unless GitHub explicitly exposes the reason.

## Promotion gates

Record evidence for:

1. current issue and repository state;
2. assignment, reservation, linked branches, and open/recent pull requests;
3. expected behavior or compatibility contract;
4. user, reliability, security, scientific, or operational impact;
5. smallest acceptable artifact;
6. regression-test or reproduction strategy;
7. focused and broader validation commands;
8. dependencies on hardware, clusters, credentials, data, or maintainers;
9. project conventions, contribution policy, and AI policy;
10. rollback, compatibility, performance, observability, and security risk.

Any failed gate moves work to `reconnaissance` or `waiting`; a numerical score
cannot override a failed gate.

## Worker contract

Every dispatch must state:

```text
Role:
Objective:
Evidence inputs:
Allowed changes:
Forbidden actions:
Validation:
Stop when:
Return:
```

Implementation starts with a failing regression test and proceeds only when it
fails for the expected reason. The smallest passing fix wins. No dependency
updates, generated agent files, unrelated formatting, speculative refactors, or
external communication.

## Completion and cleanup gates

End at a resumable boundary: dossier complete, failure reproduced, regression
test failing correctly, minimal patch passing, validation complete, review
recorded, or PR text prepared.

Write a handoff with objective, completed evidence, current diff, exact next
action, risks, unanswered questions, and explicit prohibitions. Before removing
a checkout, confirm valuable work is committed, pushed, or exported. A
read-only observer reports cleanup candidates; a human-authorized worker
performs cleanup. Use the repository's native worktree removal command, prune
metadata, clean bounded build/test caches, and verify unrelated changes remain
untouched.
