# Lightkurve #1531 — optional filters can break exact TIC identity

## Identity

- Repository: `lightkurve/lightkurve`
- Issue:
  [#1531](https://github.com/lightkurve/lightkurve/issues/1531)
- Upstream commit inspected: `3c9c0fe170b270cbd0ac74549c18919c0efd50d2`
- Checked at: `2026-07-19T03:48:16Z`
- Ownership: open, unassigned, no linked development work, and no matching open
  pull request found
- Coordination risk: reporter `@orionlee` remains engaged, supplied the detailed
  root-cause triage, and proposed removing fallback. Recheck their implementation
  intent before claiming work even if the issue remains formally unassigned.

## Scientific and operational impact

Lightkurve is used to select Kepler and TESS time-series products for scientific
analysis. A no-radius lookup for an exact TIC identifier can return a product
belonging to a different, nearby TIC when an optional author filter removes the
requested target's observation before Lightkurve decides whether to fall back to a
cone search.

The issue reports that `search_targetpixelfile("TIC 203892751", author="SPOC")`
returns a SPOC target-pixel file for nearby TIC 203892745. The two catalog objects
are about 4.5 arcseconds apart. Treating the neighbor as the requested star is a
data-provenance and source-confusion failure, not merely a display problem.

## Evidence boundary

The current MAST response and returned product are issue-reported; this
reconnaissance did not install Lightkurve or replay the live archive query. The
control-flow defect is source-established:

1. `_search_products` passes `provenance_name`, exposure time, sequence number,
   project, and data-product type into `_query_mast`.
2. `_query_mast` includes those criteria in the exact `target_name` query.
3. If that filtered query is empty, it performs a cone search using the same
   criteria.
4. In the reported case, `author="SPOC"` filters out the exact target's QLP
   observation, so the fallback finds a nearby target that does have a SPOC
   observation.

The issue's detailed triage records exactly that sequence: one exact QLP
observation without the author filter, zero exact observations with
`author="SPOC"`, and a nearby SPOC result after fallback.

## Established public contract

Merged [PR #796](https://github.com/lightkurve/lightkurve/pull/796) introduced
strict mission-specific identifier searches to prevent source confusion. Its
maintainer-authored contract is:

- without `radius`, a KIC, EPIC, or TIC lookup returns products known under the
  corresponding exact MAST `target_name`;
- with an explicit `radius`, Lightkurve performs a cone search and may return
  nearby or overlapping targets.

The current `test_overlapping_targets_718` retains both sides of that contract:
no-radius identifier searches assert one exact target, while `radius=1 arcsec`
asserts that overlapping targets are also returned.

Therefore #1531 contains two different cases:

- `author="SPOC"` with no radius is a credible identity bug and violates the
  strict-target contract;
- an explicitly supplied radius selecting nearby targets is documented behavior,
  even when the radius value appears extremely small. That case is not part of
  the actionable fix.

The explicit-radius example still exposes a separate archive anomaly: the issue
reports MAST returning the approximately 4.5-arcsecond neighbor with
`distance=0.0` for a `0.00001`-arcsecond cone. Lightkurve passes the radius into
MAST and does not independently recompute catalog separation. Isolate the MAST
resolver, observation coordinates, and `s_region` behavior before treating that
result as another Lightkurve defect.

## Why the fallback cannot simply be deleted

In the discussion for
[#1073](https://github.com/lightkurve/lightkurve/issues/1073#issuecomment-845391299),
a maintainer explains that Lightkurve originally always used cone search, then
changed to exact identifier matching because overlapping targets caused users to
request one target and receive another. The maintainer confirms that the retained
fallback runs only after the exact match fails and produces less surprising
results overall.

An
[earlier participant in the same discussion](https://github.com/lightkurve/lightkurve/issues/1073#issuecomment-845378924)
suggests that a failed exact TIC lookup likely represents an FFI-only target and
that cone fallback remains useful in that case. Treat that FFI explanation as a
design hypothesis to preserve and validate, not as a maintainer-authored contract.

The fix proposed in the #1531 discussion—remove fallback entirely—would therefore
discard an intentional compatibility path.

## Source map

At inspected commit `3c9c0fe`:

- `src/lightkurve/search.py::_search_products` constructs
  `dataproduct_type=["cube", "timeseries"]` and forwards author, mission,
  exposure-time, and sector/campaign criteria to `_query_mast`;
- `_query_mast` recognizes exact KIC, EPIC, and TIC identifiers;
- when `radius is None`, it calls
  `Observations.query_criteria(target_name=exact_target_name, **query_criteria)`;
- any zero-row response triggers
  `Observations.query_criteria(objectname=target, ...)`, which changes the
  selection from identifier identity to sky overlap;
- `_filter_products` later performs file-extension and cadence filtering, but
  provenance filtering has already affected observation selection.

The failure is thus a conflation of two questions:

1. Does this exact target have an observation identity that prevents source
   confusion?
2. Does that target have a product matching the user's optional filters?

An empty answer to question 2 currently causes Lightkurve to answer question 1
with a cone search.

## Smallest future regression shape

Add a deterministic, non-remote test around `_query_mast` or the smallest public
search boundary. Mock `Observations.query_criteria` so the fixture contains:

- an exact TIC observation with QLP provenance;
- no exact observation after applying `provenance_name=["SPOC"]`;
- a nearby TIC with SPOC provenance that a cone search would return.

For `radius=None`, assert:

1. the result is empty for the requested SPOC product;
2. no `objectname` cone query is used after the exact target is known to exist;
3. no row for the neighboring `target_name` can escape.

Add two controls:

- when the exact target genuinely does not exist, the historical cone-search
  fallback remains available;
- when the caller explicitly supplies `radius`, cone-search behavior and nearby
  results remain unchanged.

The regression should not rely solely on current MAST contents. The existing
search suite is largely marked `remote_data`; a mocked test is necessary to make
the identity invariant stable and CI-reproducible.

## Narrow implementation boundary

The likely production boundary is `_query_mast`:

- preserve the exact query with all requested filters as the fast path;
- if it is empty, distinguish “the exact target identity is absent” from “the
  exact target exists but optional filters produced no match”;
- return an empty exact-target result in the latter case;
- invoke cone fallback only in the former case;
- leave all explicit-radius calls unchanged.

A minimal existence probe should retain criteria that define the search domain,
such as project and relevant data-product class, while excluding optional filters
such as provenance, sequence number, and exposure time. The exact criterion split
must be verified against the FFI-only fallback and cross-mission identifier tests
before production code is changed.

Do not move all filtering blindly into `_filter_products`: it does not currently
implement complete observation-level provenance, sector, or project filtering.

## Resource assessment

- Reproduction strategy: mocked tables; CPU-only; no archive download
- Local environment: `lightkurve`, `astroquery`, and `astropy` are absent
- Filesystem rechecked at `2026-07-19T03:54:17Z`: 97% used, about 16 GiB
  available
- Action taken: source and history inspection only; no clone or dependency install

The future test should use the project's declared environment in a disposable
checkout after the implementation slot becomes free.

## Decision

- Status: reconnaissance complete; waiting for implementation capacity
- Importance: high scientific-data integrity
- Contract clarity: sufficient for a bounded fix
- Evidence quality: GO for the scoped no-radius author-filter defect
- Implementation design: bounded, with the identity-probe criterion split to be
  fixed by tests
- Ready for dispatch: no; BuildKit PR #6966 occupies the sole implementation slot
- Exact next action: revalidate issue ownership, matching pull requests, current
  source, reporter intent, and the active implementation slot; then add the
  deterministic identity regression before changing `_query_mast`
- Handoff:
  [`.contrib/handoffs/lightkurve-1531.md`](../handoffs/lightkurve-1531.md)
- Implementation gate: do not write a Lightkurve test or production change until
  the Observer Manager reports a free slot
- External-action gate: do not contact maintainers, claim the issue, push, or open
  a pull request without explicit user authorization
