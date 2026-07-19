# Lightkurve #1531 reconnaissance handoff

## Objective

Prevent a no-radius search for an exact KIC, EPIC, or TIC identifier from
returning another target merely because optional search filters remove all
matching observations for the requested target.

## Completed

- Revalidated
  [lightkurve/lightkurve #1531](https://github.com/lightkurve/lightkurve/issues/1531)
  at `2026-07-19T03:48:16Z`: open, unassigned, with no linked development work
  and no matching open pull request found.
- Inspected upstream commit
  `3c9c0fe170b270cbd0ac74549c18919c0efd50d2`.
- Mapped the failure to `src/lightkurve/search.py::_query_mast`: optional
  observation filters participate in the exact-target query, and an empty
  filtered result changes the query mode to a cone search.
- Confirmed from merged
  [PR #796](https://github.com/lightkurve/lightkurve/pull/796) and
  `test_overlapping_targets_718` that no-radius mission identifiers are strict,
  while an explicit radius intentionally permits nearby targets.
- Confirmed from the
  [#1073 maintainer discussion](https://github.com/lightkurve/lightkurve/issues/1073#issuecomment-845391299)
  that exact-first behavior with fallback after a genuine exact-match failure is
  intentional; it must not be removed wholesale.
- Recorded the separate
  [FFI-only hypothesis](https://github.com/lightkurve/lightkurve/issues/1073#issuecomment-845378924)
  from an earlier participant as a path requiring validation, not a confirmed
  maintainer contract.
- Defined a deterministic mocked-observation regression that does not depend on
  mutable MAST contents or large scientific datasets.
- Avoided a clone and dependency installation because source-level evidence was
  sufficient and local storage is at high risk.

## Evidence

The issue-reported archive state for sector 80 is:

```text
requested target: TIC 203892751
requested target products: QLP light curve; no target-pixel file
nearby target: TIC 203892745, about 4.5 arcseconds away
nearby products: SPOC target-pixel file and SPOC/QLP light curves
```

The reported no-radius call
`search_targetpixelfile("TIC 203892751", author="SPOC")` follows this path:

```text
exact target_name + SPOC filter -> zero observations
zero observations -> cone fallback
cone fallback + SPOC filter -> nearby TIC 203892745
product filtering -> one nearby target-pixel file
```

This remote result is issue-reported. The control-flow path and the contract
violation are established by current source and merged history.

Detailed artifact:
[`lightkurve-1531.md`](../dossiers/lightkurve-1531.md).

## Next exact action

After the Observer Manager reports a free implementation slot:

1. Recheck issue state, assignee, comments, linked development work, matching
   open pull requests, current `main`, and whether the engaged reporter intends
   to implement their proposed change.
2. Create a disposable checkout and use only project-declared test dependencies.
3. Add a non-remote regression with mocked `Observations.query_criteria`
   responses:
   - exact target exists with QLP provenance;
   - exact target plus `author="SPOC"` is empty;
   - cone search would return a nearby SPOC target.
4. Assert that a no-radius exact-ID lookup returns empty and never accepts the
   nearby target.
5. Preserve controls proving that a genuinely absent exact target can still use
   fallback and that an explicit radius still performs a cone search.
6. Make the smallest `_query_mast` change that separates target-identity
   existence from optional filtering.
7. Run the focused search tests, the existing remote-data controls when network
   policy permits, and the repository's formatting and lint checks.
8. Remove the disposable checkout after preserving a patch and validation
   evidence if publication is not yet authorized.

## Risks or unanswered questions

- The exact “identity existence” criteria need validation. Retaining project and
  data-product class while omitting provenance, sequence number, and exposure
  time is the strongest initial hypothesis.
- A target with no exact observation may depend on fallback for FFI-derived
  products; that is a discussion-based hypothesis and must remain covered while
  its current behavior is validated.
- `_filter_products` is not a drop-in replacement for every observation-level
  filter, so a broad filter relocation would expand scope.
- Live MAST contents can change and the existing remote tests are not a durable
  regression oracle.
- The issue also reports surprising results with explicit `radius`, but merged
  project history defines that behavior as intentional.
- The issue reporter remains active, supplied the root-cause triage, and recently
  merged related exact-TIC work in PR #1541. Formal assignment is empty, but
  contributor intent must be rechecked before claiming the issue.
- MAST reports the approximately 4.5-arcsecond neighbor at `distance=0.0` in the
  explicit-radius example. That archive/resolver anomaly requires separate
  isolation and is not evidence for changing Lightkurve's radius contract.

## Do not do

- Do not remove cone-search fallback globally.
- Do not change explicit-radius semantics as part of this issue.
- Do not accept `distance == 0` as proof of target identity; compare the exact
  MAST `target_name`.
- Do not add a live-MAST-only regression.
- Do not refactor unrelated search, download, or cache behavior.
- Do not begin implementation while BuildKit PR #6966 occupies the sole slot.
- Do not contact maintainers, claim the issue, push a branch, or open a pull
  request without explicit user authorization.
