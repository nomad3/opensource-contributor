# Gammapy #6716 reader-compatibility handoff

## Objective

Allow the Gammapy 2.0.x maintenance line to identify and read a
`SpectrumDatasetOnOff` GADF payload written by 2.1 through the ordinary
markerless `Datasets.read()` path, without changing the 2.0.x OGIP writer
default.

## Completed

- Revalidated [Gammapy #6716](https://github.com/gammapy/gammapy/issues/6716)
  as open, unassigned, labeled `bug`, and targeted to milestone `2.0.2`.
- Found no linked or matching pull request, branch, or commit.
- Pinned and compared `v2.0.1`, current `v2.0.x`, `v2.1`, current `v2.1.x`,
  and current `main`.
- Traced `Datasets.read()` through registry dispatch and
  `SpectrumDatasetOnOff.from_dict()` to the no-format `read()` call.
- Confirmed that dataset YAML records no format marker.
- Confirmed that 2.0.x already supports an explicit GADF read but defaults a
  markerless read to OGIP.
- Confirmed that 2.1 writes GADF by default and detects GADF through
  `COUNTS_BANDS`.
- Mapped the behavior to merged
  [PR #5812](https://github.com/gammapy/gammapy/pull/5812).
- Designed a synthetic, offline, markerless-YAML regression that requires no
  `gammapy-data`.
- Classified the 2.0.x-generated fixture as a dispatch proxy and preserved a
  separate pinned-2.1 producer acceptance control for true cross-version
  validation.
- Mapped Gammapy's mandatory issue-discussion, DCO, test, and AI-disclosure
  requirements.

Detailed evidence:
[`gammapy-6716.md`](../dossiers/gammapy-6716.md).

No checkout, environment, dependency, fixture, source change, or upstream
mutation was created. The issue-reported failure was not runtime-reproduced in
this cycle.

## Next exact action

Only after BuildKit PR #6966 releases the implementation slot and the user
authorizes upstream contact:

1. Recheck #6716 comments, assignment, linked development, matching pull
   requests and branches, and current `v2.0.x`/`v2.1.x` heads.
2. Have the human contributor write an original issue comment asking whether
   maintainers want a direct reader-only 2.0.x change that preserves the OGIP
   writer default.
3. Wait for maintainer direction before creating a branch or code.
4. Build a disposable development environment only if storage remains safe.
5. Add the 2.0.x-generated synthetic GADF payload plus markerless YAML
   regression first, label it as a dispatch proxy, and demonstrate the current
   missing-`EBOUNDS` failure.
6. Add the smallest accepted reader-format detection.
7. In a separate pinned-2.1 producer environment, write the same synthetic
   bundle through the ordinary default path; read that untouched output in the
   candidate 2.0.x environment.
8. Prove markerless GADF and OGIP reads, explicit-format compatibility,
   preserved 2.0.x `ogip-sherpa` behavior, malformed-layout behavior, and the
   shared-field round trip.
9. Run the exact test node, the spectrum test module, `tox -e test`, and scoped
   pre-commit checks.
10. Write the required release note and disclose AI assistance accurately.

## Risks and unanswered questions

- The `2.0.2` milestone suggests a maintenance fix but does not define whether
  the pull request should target `v2.0.x` directly.
- A literal 2.1 detector backport may narrow the 2.0.x handling of explicit
  `ogip-sherpa`; preserve the current maintenance behavior with a regression.
  This is not a contract blocker unless maintainers specifically request the
  2.1 rejection behavior.
- A successful dispatch fix does not prove all newer GADF features can be
  represented in 2.0.x. A 2.0.x-written GADF file is only a dispatch proxy;
  require the pinned-2.1 producer control, test only shared supported fields,
  and document any additional boundary separately.
- A `SPECTRUM` extension with missing `HDUCLASS` needs an intentional error, not
  an accidental `KeyError` or an overbroad recovery heuristic.
- Adjacent issue #6522 owns broader format propagation and must stay out of
  scope.
- The full dependency stack was not installed, and the issue-reported failure
  was not executed locally.

## Do not do

- Do not begin a second implementation while BuildKit #6966 occupies the sole
  slot.
- Do not comment on or claim the issue without explicit user authorization.
- Do not code before the mandatory Gammapy issue discussion and maintainer
  response.
- Do not switch the 2.0.x writer default to GADF as part of this repair.
- Do not redesign dataset YAML, generic bundle I/O, or #6522's format model.
- Do not claim complete cross-version compatibility from a format-dispatch
  regression.
- Do not paste AI-generated code, prose, or comments upstream; any contribution
  must be human-written, understood, validated, signed off, and disclosed.
