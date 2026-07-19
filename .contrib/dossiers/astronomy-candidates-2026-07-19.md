# Astronomy open-source candidate scan

## Objective

Identify community-driven astronomy projects where Python, data engineering,
SRE, DevOps, and AI-assisted testing skills can solve scientifically meaningful
problems without requiring immediate expertise in astrophysical modeling.

Compiled from public checks completed on 2026-07-19; Bilby was revalidated at
`2026-07-19T03:37:37Z`, Lightkurve #1531 at `2026-07-19T03:52:11Z`, and yt
#5439/PR #5440 at `2026-07-19T04:01:37Z`. The second audit round checked SunPy
#8599 at `2026-07-19T05:19:11Z`, Gammapy #6716 at
`2026-07-19T05:15:10Z`, Dask #12507 at `2026-07-19T04:32:12Z`, and
Lightkurve #1565 at `2026-07-19T05:27:48Z`.
GWPy #1850 received a source, history, policy, and ownership audit at
`2026-07-19T05:59:41Z`; Astropy #18910 received the same bounded audit at
`2026-07-19T06:40:44Z`.

This is a non-authoritative lead inventory, not an operational queue. Only the
Observer Manager may promote or dispatch an item. Bilby #1114, Lightkurve
#1531 and #1565, yt #5439, Dask #12507, Gammapy #6716, GWPy #1850, and SunPy
#8599 have received deeper audits. Astropy #18910 now also has a full
source-only dossier. The remaining entries are issue-level leads that still
require a fresh evidence bundle with exact timestamps,
assignment/overlap searches, resource requirements, and recheck conditions
before promotion.

## Project ranking

| Priority | Project | Best contribution lane | Rationale |
| --- | --- | --- | --- |
| 1 | Bilby and GWPy | Gravitational-wave inference and signal processing | Bilby's arithmetic overwrite is locally reproduced; GWPy's supplied-ASD length failure and adjacent silent-shortening regime are source-confirmed. Both target risks in expensive analyses. |
| 2 | Lightkurve | TESS/Kepler archive and time-series correctness | Wrong-target and nondeterministic-product bugs directly threaten dataset selection. |
| 3 | Dask and xarray | Scientific-pipeline determinism and scalability | The hash-seed optimizer defect is locally reproduced and affects graph construction for survey, remote-sensing, and other chunked-array workloads. |
| 4 | yt | Scalable simulation analysis | Excellent match for data correctness, Dask, memory, performance, and very large datasets. |
| 5 | Gammapy | Dataset compatibility and CI | Scientific results depend on stable serialization, numerical correctness, and dependency compatibility. |
| 6 | Astropy ecosystem | Core data formats, archive access, and coordinates | Foundational impact and strong review standards; the singleton table-stack ownership defect now has a bounded contract dossier. |
| 7 | Survey-scale infrastructure | LSDB, HATS, SkyPortal, Fink, and RAIL | Strategic data/ML infrastructure fit; issue selection requires deeper setup and coordination. |

## Candidate issues

| Project | Candidate | Evidence state | Assessment |
| --- | --- | --- | --- |
| Bilby | [#1114 — BNS conversion overwrites valid `lambda_1=0`](https://github.com/bilby-dev/bilby/issues/1114) | Arithmetic overwrite locally reproduced and source-inspected; downstream failure issue-reported; [full dossier](bilby-1114.md) | Open, unassigned, and no linked development work at the timestamp above. The reproduced roundoff is the reported failure mechanism; the issue reports LALSimulation rejecting it after a long inference. Mixed-representation semantics need maintainer confirmation. |
| Lightkurve | [#1531 — exact TIC search can return a nearby target](https://github.com/lightkurve/lightkurve/issues/1531) | Current source and historical contract mapped; remote result issue-reported; offline regression designed; [full dossier](lightkurve-1531.md) | The no-radius author-filter path violates strict target identity; explicit-radius neighbors are documented behavior. Evidence is GO, but dispatch waits for the implementation slot and a fresh check of the engaged reporter's intent. |
| Lightkurve | [#1565 — `download_all()` returns a nondeterministic subset of TESS products](https://github.com/lightkurve/lightkurve/issues/1565) | Current source mapped; core developer reproduced; offline regression designed; contributor intent overlap | Fresh download opens only `cutout_path[0][0]`; cache constrains matches to the first `get_sectors()` detector prefix and opens `cached_files[0]`, selecting the target-center detector in the reported single-row case but providing no general multi-detector tie-break. `Sammy-Dabbas` has offered to implement, so wait and do not duplicate. |
| yt | [#5439 — GIZMO frontend fails on empty particle chunks](https://github.com/yt-project/yt/issues/5439) | Overlap confirmed; assigned reporter owns active [PR #5440](https://github.com/yt-project/yt/pull/5440); [read-only review](../reviews/yt-5440.md) | Do not duplicate. The guard is narrow, but an unresolved reviewer request remains and the FIRE-only regression is excluded or skipped by ordinary CI. A deterministic cosmological empty-chunk test is mapped for the existing author. |
| GWPy | [#1850 — whitening short time series fails with a supplied ASD](https://gitlab.com/gwpy/gwpy/-/work_items/1850) | Three pinned versions source-audited; exact length algebra and future regression designed; independently reviewed; [full dossier](gwpy-1850.md) | A supplied ASD can yield an impulse below half the requested taps and broadcast-fail; the adjacent range silently returns fewer taps. Evidence GO, but exact reporter inputs, maintainer semantics, and the implementation slot remain blockers. |
| Dask | [#12507 — optimized graph depends on `PYTHONHASHSEED`](https://github.com/dask/dask/issues/12507) | Locally reproduced on 2026.7.1, phase-traced, source-inspected, and independently reviewed; [full dossier](dask-12507.md) | Seeds 0–7 produced 334–728 optimized tasks locally. PR #11899 removed per-layer key filtering; restoring it yields 82 tasks across every seed and correct computed output. Open, unassigned, and untriaged; evidence GO, dispatch WAIT. |
| Gammapy | [#6775 — SVD failures with the current scientific Python stack](https://github.com/gammapy/gammapy/issues/6775) | Issue-reported lead; public ownership/overlap checked on scan date | The report shows gamma-ray response-map failures with a new dependency stack. Reduce the WCS matrix failure and locate the Gammapy/Regions/dependency boundary. |
| Gammapy | [#6716 — Gammapy 2.0.1 cannot read a dataset written by 2.1](https://github.com/gammapy/gammapy/issues/6716) | Pinned release/maintenance source matrix and markerless-YAML call path; dispatch proxy plus 2.1-producer acceptance control designed; independently reviewed; [full dossier](gammapy-6716.md) | Milestone 2.0.2 supports a maintenance fix. The old reader defaults to OGIP despite already supporting explicit GADF, so 2.1 output fails at missing `EBOUNDS`. Evidence is GO; dispatch waits for mandatory issue discussion, target direction, and the implementation slot. |
| Gammapy | [#6787 — CI not running correctly on development dependencies](https://github.com/gammapy/gammapy/issues/6787) | Direct overlap found | Draft [PR #6731](https://github.com/gammapy/gammapy/pull/6731) covers the development-dependency CI lane; observe and do not duplicate. |
| SunPy | [#8599 — GOES-19 CCOR science data does not load as a map](https://github.com/sunpy/sunpy/issues/8599) | Current/stable source and contract history mapped; synthetic multi-HDU regression designed | A second 2-D HDU is invalid for `Map`; `allow_errors=True` loads the valid science HDU and default fail-fast behavior is historically intentional. Treat code as no-go unless maintainers request a narrow file-derived auxiliary-HDU exception. |
| Astropy | [#18910 — one-table stack returns the caller's table despite documenting a new table](https://github.com/astropy/astropy/issues/18910) | Pinned main/`v8.0.1` source, tests, history, policy, and overlap audited; independently reviewed; [full dossier](astropy-18910.md) | The identity alias and top-level metadata effect are verified. Evidence is GO; dispatch waits for table-maintainer decisions on copy depth, vstack-only versus all operations, singleton `dstack` rank/index behavior, release treatment, and the implementation slot. |
| yt | [#2281 — faster particle depositions](https://github.com/yt-project/yt/issues/2281) | Issue-reported benchmark lead | Performance-sensitive and broad. Requires fresh ownership/overlap checks, representative datasets, and baseline evidence. |
| SunPy | [#8416 — support arbitrary APE-14 WCS in `GenericMap.plot`](https://github.com/sunpy/sunpy/issues/8416) | Overlap found | Do not duplicate: active [PR #8684](https://github.com/sunpy/sunpy/pull/8684) implements the requested support. |
| Astroquery | [#3626 — VizieR errors appear as empty results](https://github.com/astropy/astroquery/issues/3626) | Overlap found | Observe only: active [PR #3632](https://github.com/astropy/astroquery/pull/3632) overlaps the error-semantics work. |
| Lightkurve | [#1564 — TGLC quality mask falsely reports corrupt data](https://github.com/lightkurve/lightkurve/issues/1564) | Overlap found | Do not duplicate: active [PR #1566](https://github.com/lightkurve/lightkurve/pull/1566) is linked to the issue. |

## Completed reconnaissance cycles

Bilby #1114:

1. The negative-roundoff overwrite was reproduced from current formulas.
2. The conversion source and existing tests were mapped.
3. Mixed-representation semantics remain unconfirmed.
4. A concise contract question is preserved in the Bilby handoff.

Lightkurve #1531:

1. The author-filter source-confusion path was mapped on current `main`.
2. PR #796 establishes strict no-radius identity and intentional radius-based
   cone search.
3. The exact-first fallback rationale and FFI-only hypothesis were attributed
   separately.
4. An offline mocked-observation regression and narrow `_query_mast` boundary are
   preserved in the Lightkurve handoff.

yt #5439 / PR #5440:

1. Explicit reporter ownership and active implementation overlap were confirmed.
2. The GIZMO empty-creation-time guard was reviewed as narrow and mechanically
   sound.
3. An unresolved reviewer request and the absence of an ordinary-CI regression
   prevent promotion.
4. A deterministic cosmological empty-chunk test design is preserved in the
   read-only PR review for the existing author.

Dask #12507:

1. The public graph was reproduced across eight isolated hash seeds on the
   reported Dask release, with seven distinct optimized task counts.
2. Same-seed repeatability and phase-by-phase counts were verified.
3. The first task-count and declared layer-topology divergence is after
   `HighLevelGraph.cull()`.
4. Restoring the per-layer output-key filter removed the variance, reduced all
   seeds to 82 tasks, and computed the expected selection; stable traversal is
   retained only as diagnostic evidence.

Gammapy #6716:

1. Release, maintenance, and main sources were pinned and compared.
2. The markerless `Datasets.read()` path was traced into the 2.0.x OGIP default,
   while explicit GADF support was confirmed to already exist on that line.
3. The 2.1 GADF writer-default change and bounded reader detection were mapped
   to merged PR #5812.
4. A synthetic no-data regression and reader-only maintenance boundary are
   preserved in the [Gammapy handoff](../handoffs/gammapy-6716.md).
5. The in-branch fixture is explicitly a dispatch proxy; a pinned-2.1 producer
   control is required before promotion.
6. The failure remains issue-reported and source-explained, not locally
   runtime-reproduced.
7. Independent adversarial review is GO.

GWPy #1850:

1. The reported traceback was matched exactly to `v3.0.12`; `v4.0.1` and
   current `main` retain the relevant length logic.
2. Source algebra proves the raw broadcast boundary and an adjacent
   silent-shortening regime.
3. The issue's operand shapes prove a 3,072-sample impulse and 8,192 requested
   taps, but not the input sample count, sample rate, duration, or ASD grid.
4. A deterministic no-data contract test is designed but was not executed.
5. Reject, shorten, and ASD-alignment semantics remain a maintainer decision.
6. Independent adversarial review is GO.

Astropy #18910:

1. Current `main` and `v8.0.1` sources confirm that singleton `vstack()`,
   `hstack()`, and `dstack()` return the exact `Table` or `QTable`.
2. Existing singleton tests compare values but do not assert identity or
   mutation isolation; `dstack()` covers only direct ordinary-`Table` input.
3. PR #3313 establishes intentional vstack/hstack identity history, while PR
   #16130 protects the caller's outer input list but does not define output
   ownership.
4. Private vstack/hstack fast paths and `dstack()`'s separate
   `(n, *cell_shape)` versus `(n, 1, *cell_shape)` rank and index contract are
   mapped.
5. A no-data 3-operation by 2-invocation by 2-table-class regression matrix is
   designed but was not executed.
6. Independent source and policy reviews are GO after correcting test,
   impact-inference, overlap, and backport claims.

Second-round astronomy-native audits:

1. Lightkurve #1565 is source-established and scientifically meaningful, but an
   external contributor has offered to implement while maintainers settle
   preferred-camera versus return-all semantics.
2. Gammapy #6716 now has a full source-backed dossier: it is a narrow 2.0.x
   reader-detection problem with a 2.0.2 milestone, not a reason to backport the
   2.1 writer-default change.
3. SunPy #8599 is not an alternate-WCS defect: default fail-fast and opt-in
   skipping are established. Only a maintainer-requested file-derived
   auxiliary-HDU exception could justify implementation.
4. Astropy #18910 is a verified singleton identity mismatch, but code must wait
   for a table-maintainer decision on copying, operation scope, `dstack` rank,
   indices, and release treatment.

The Observer may continue read-only monitoring. Upstream contact requires explicit
user authorization. Bilby implementation additionally requires maintainer-defined
mixed-input semantics. GWPy requires the reporter's exact inputs and
maintainer-selected compatibility semantics. Lightkurve implementation requires a
free Observer slot and a fresh reporter-intent and overlap check. Dask and Gammapy
require a free slot and fresh maintainer/overlap checks. Astropy requires its
table ownership and rank contract before code. yt #5439 must remain observe-only
while PR #5440 is active.

## Non-authoritative research inventory

These categories summarize potential research depth only. They do not confer
`ready`, `waiting`, or dispatch status.

### Bounded leads

- Bilby #1114 — highest scientific consequence with the cheapest reproduction.
- Lightkurve #1531 — no-radius wrong-target selection; evidence is GO and an
  offline deterministic fixture is designed, but dispatch is waiting.
- GWPy #1850 — [source-confirmed impulse/tap compatibility gap](gwpy-1850.md);
  evidence GO, dispatch WAIT on reporter metadata, maintainer semantics, and
  the implementation slot.
- Gammapy #6775 — reduce dependency-sensitive WCS/SVD failures.
- Gammapy #6716 — [bounded GADF reader detection](gammapy-6716.md) for the
  2.0.x maintenance line; evidence GO, dispatch WAIT.
- Astropy #18910 — [source-confirmed singleton table alias](astropy-18910.md);
  evidence GO, dispatch WAIT on ownership, copy depth, operation, `dstack`
  rank/index, release-line semantics, and the implementation slot.

### Deep research

- Dask #12507 — locally reproduced cull-order sensitivity with extreme
  issue-reported production impact.
- yt #2281 — particle-deposition benchmark and algorithm mapping.
- [katdal #392](https://github.com/ska-sa/katdal/issues/392) — Dask/xarray
  serialization is important, but the reporter owns overlapping
  [draft PR #389](https://github.com/ska-sa/katdal/pull/389); observe rather
  than duplicate.
- [arcae #220](https://github.com/ratt-ru/arcae/issues/220) — storage-manager
  cache sizing requires C++/Cython/casacore,
  representative Measurement Set and Ray evidence, and coordination with
  active maintainer-led adjacent xarray-ms work.

### Overlap, policy, or resource risks

- Astroquery #3626 — active [PR #3632](https://github.com/astropy/astroquery/pull/3632).
- SunPy #8416 — active [PR #8684](https://github.com/sunpy/sunpy/pull/8684).
- Lightkurve #1564 — active [PR #1566](https://github.com/lightkurve/lightkurve/pull/1566).
- yt #5439 — assigned reporter owns active
  [PR #5440](https://github.com/yt-project/yt/pull/5440); observe its unresolved
  review and test-coverage gap.
- Lightkurve #1565 — contributor `Sammy-Dabbas` offered to implement; await
  maintainer response and final download semantics.
- Gammapy #6787 — draft
  [PR #6731](https://github.com/gammapy/gammapy/pull/6731) directly overlaps
  the development-dependency CI work.
- SunPy #8599 — member-reporter intent is high, and established fail-fast plus
  `allow_errors=True` semantics make a global default-skip patch no-go without
  explicit maintainer reversal or a narrower file-only contract.
- Astropy #11148's original diagnostic bug is already fixed, and a core
  maintainer owns the remaining structured-column flatten feature.
- yt #5457 — important segmentation fault, but the approximately 0.9-GB reproducer
  is not publicly attached.
- Gammapy #6716 — reader-only detection versus broader backport surface needs
  maintainer confirmation.
- Lightkurve #1531 — the engaged reporter supplied detailed triage and recently
  merged related PR #1541; recheck their intent before claiming work.

## Longer-term astronomy infrastructure lane

- resilient archive/catalog access with explicit transient versus permanent errors;
- cache correctness and provenance for remote scientific data;
- FITS, Zarr, and object-storage interoperability;
- Dask-backed analysis of survey and simulation datasets;
- reproducible workflow execution with Snakemake, Airflow, Flyte, or Argo;
- OpenTelemetry instrumentation for long-running scientific pipelines;
- AI agents for literature/data discovery only when outputs remain cited,
  reproducible, and human-verifiable.

## Decision

- Completed reconnaissance: Bilby #1114, Lightkurve #1531, Dask #12507,
  Gammapy #6716, source-only GWPy #1850, and source-only Astropy #18910;
  fresh bounded audits also cover Lightkurve #1565 and SunPy #8599
- Best data-integrity implementation after slot and ownership recheck:
  Lightkurve #1531
- Best astronomy-native maintenance candidate after slot and contract recheck:
  Gammapy #6716
- Best bounded gravitational-wave preprocessing investigation: GWPy #1850;
  implementation waits for exact inputs and maintainers' scientific contract
- Best bounded core astronomy table/API contract: Astropy #18910;
  implementation waits for table-maintainer decisions and the free slot
- Bounded simulation implementation candidate: reselection required; yt #5439
  is already owned by active PR #5440
- Best evidence-backed cross-science performance lane: Dask #12507
- Observe, do not duplicate: Astroquery #3626, SunPy #8416, Lightkurve #1564,
  Lightkurve #1565 while contributor intent is active, Gammapy #6787, and yt
  #5439
- No upstream issue was claimed or commented on during this scan
- None of these leads is authorized for implementation by this inventory
