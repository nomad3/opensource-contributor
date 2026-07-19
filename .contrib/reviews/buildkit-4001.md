# BuildKit #4001 cross-review

## Reviewers

- Fable 5: initial reconnaissance and adversarial review
- Codex: independent `gh`/source validation, dossier correction, and final consistency check

## Findings and resolution

### Blocking

- **Tracker listed #4001 in both `ready` and `waiting`.**
  Resolved by removing the ready entry. It now appears only in `waiting`.

### Important

- **The dossier called BuildKit's default branch `main`.**
  Resolved to `master`, verified from the remote and local checkout.
- **Related PRs were described only as closed.**
  Resolved with exact states: #6874 and #6958 merged, #6918 closed unmerged, and
  #6588 open.
- **Evidence dates mixed UTC and local dates.**
  Resolved to the local workspace date, 2026-07-18.

### Optional

- **Security-policy citation was imprecise.**
  Resolved by citing `.github/SECURITY.md` and the corresponding public instructions in
  `.github/CONTRIBUTING.md`.
- **`make validate-docs` was broader than the README-only scope.**
  Removed from the exact validation set; `make validate-doctoc` is the relevant docs
  gate.
- **`blocked` in the dossier and `waiting` in the tracker appeared different.**
  No change: the repository operating model intentionally returns blocked work to the
  waiting queue.

## Verdict

The blocked decision is justified. The evidence is sufficient to resume later, the
tracker no longer permits accidental selection, no BuildKit file was modified, and no
upstream communication occurred.
