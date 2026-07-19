# Gammapy #6775 — Regions 0.12 triggers SVD failures in diagonal EDisp tests

## Identity

- Repository: `gammapy/gammapy`
- Issue:
  [#6775](https://github.com/gammapy/gammapy/issues/6775)
- Issue state: open, labeled `bug`, unassigned, no milestone, zero comments,
  and no linked development
- Reporter: `olebole`
- Reported stack: Gammapy 2.1, Astropy 8.0.0, Regions 0.12, NumPy 2.4.6,
  and SciPy 1.17
- Current Gammapy `main` inspected:
  [`6ed4106`](https://github.com/gammapy/gammapy/commit/6ed4106cbe6b2c8b045258770d6c46f1aabe6282)
- Current Gammapy `v2.1.x` inspected:
  [`531ec55`](https://github.com/gammapy/gammapy/commit/531ec555024a17fdb6d99276e765265bc1bf13d9)
- Gammapy `v2.1` release inspected:
  [`03f65e0`](https://github.com/gammapy/gammapy/commit/03f65e08ac04741ff5f1f7b1aeed20dddeac2023)
- Regions `v0.11` inspected:
  [`988b267`](https://github.com/astropy/regions/commit/988b2672817942796351b5d0da8e80596541f2df)
- Regions `v0.12` inspected:
  [`f6919cc`](https://github.com/astropy/regions/commit/f6919cc882e752d788e815cb35285ca3126d5260)
- Current Regions `main` inspected:
  [`e3216a4`](https://github.com/astropy/regions/commit/e3216a48d46554c74c148a5be038534a32b046d2)
- Live ownership, overlap, source, history, dependency, and policy check:
  `2026-07-19T07:04:14Z`

## Decision boundary

The released-stack failure is real and the source path is bounded. The correct
repair owner and compatibility contract are not established.

Gammapy 2.1 creates a synthetic two-by-one all-sky CAR geometry with
180 degrees per pixel for a diagonal energy-dispersion response. Asking for the
response at a point converts that point into a `RegionGeom`; obtaining the
point geometry's center then converts a fallback one-pixel rectangle back to
sky coordinates. Regions 0.12 routes that rectangle conversion through a new
local Jacobian and SVD path whose nominal one-pixel samples are 180-degree
steps on this geometry.

The issue reports three failures with an `invalid value` reaching NumPy's SVD.
Pinned source predicts that at least one fixed one-pixel sample can leave the
valid CAR latitude domain or make the local tangent transformation
non-invertible. That prediction is a source inference consistent with the
traceback, not a local reproduction or a recorded numerical matrix.

Current Gammapy contains the problem by excluding Regions 0.12, Astropy 8, and
SciPy 1.18. The affected call path and tests remain in source. A dependency cap
is therefore containment, not evidence that either project has repaired the
underlying geometry boundary.

Decision: **GO for this source-only dossier; WAIT for runtime work,
implementation, and upstream contact.** BuildKit PR #6966 remains the
portfolio's sole active implementation.

## Scientific and operational impact

Energy dispersion describes how reconstructed gamma-ray energy is distributed
relative to true energy. The reported exception prevents construction and
validation of diagonal energy-dispersion kernels on the reported scientific
Python stack. The same traceback boundary appears in response conversion,
stacking, and quick-look tests listed by the reporter.

Verified impact:

- Gammapy 2.1 package-build CI fails on the reported dependency stack;
- the existing synthetic diagonal-response test fails before it can validate
  kernel normalization;
- current Gammapy excludes the triggering dependency versions, preventing
  users from combining the latest admitted releases in one resolved
  environment.

Inferred impact:

- downstream environments that override the caps can encounter the same
  failure when extracting a diagonal response at a point;
- delayed support for current Astropy and Regions releases increases
  maintenance and integration pressure for gamma-ray analysis environments.

This is a loud failure. No silent numerical corruption, wrong published
result, real observation failure, or frequency in user workloads was
established.

## Pinned dependency and source matrix

| Gammapy line | Dependency contract | Relevant source |
| --- | --- | --- |
| `v2.1` at `03f65e0` | `astropy>=6.1.5`, `regions>=0.9.0`, `scipy>=1.13`; admits the reported stack | Two-by-one CAR geometry, point-region conversion, and four-position test are present |
| `v2.1.x` at `531ec55` | Same unbounded upper ranges | Relevant call path and test remain present |
| `main` at `6ed4106` | `astropy>=6.1.5,<8.0`, `regions>=0.9.0,<0.12`, `scipy>=1.13,<1.18` | Relevant call path and test remain present, but the resolver excludes the reported stack |

Pinned dependency files:

- [Gammapy v2.1 `pyproject.toml`](https://github.com/gammapy/gammapy/blob/03f65e08ac04741ff5f1f7b1aeed20dddeac2023/pyproject.toml)
- [current `v2.1.x` `pyproject.toml`](https://github.com/gammapy/gammapy/blob/531ec555024a17fdb6d99276e765265bc1bf13d9/pyproject.toml)
- [current `main` `pyproject.toml`](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/pyproject.toml)

The caps landed in two containment changes:

1. [Gammapy PR #6737](https://github.com/gammapy/gammapy/pull/6737),
   merged as
   [`df7a20a`](https://github.com/gammapy/gammapy/commit/df7a20a65de929e4606992824d52f8366459fbc4),
   temporarily added `astropy<8.0` and `scipy<1.18` for the related
   development-dependency failures in #6736.
2. [Gammapy PR #6748](https://github.com/gammapy/gammapy/pull/6748),
   merged as
   [`76f760b`](https://github.com/gammapy/gammapy/commit/76f760b2081257fa4c4201267ec8e031e3f46cfe),
   added `regions<0.12` and restored data-backed development-dependency CI.
   Its author reported that the Regions cap resolved the remaining CI
   problem.

That history makes Regions 0.12 the strongest public change boundary. It does
not prove whether the durable fix belongs in Regions, Gammapy, or both.

## Exact cross-project call path

The reported path can be followed entirely through pinned source:

1. Gammapy
   [`EDispMap.get_edisp_kernel()`](https://github.com/gammapy/gammapy/blob/03f65e08ac04741ff5f1f7b1aeed20dddeac2023/gammapy/irf/edisp/map.py#L108-L115)
   calls `to_region_nd_map(region=position)`.
2. `IRFMap.to_region_nd_map()` delegates to the underlying WCS map.
3. The point branch in
   [`WcsNDMap.to_region_nd_map()`](https://github.com/gammapy/gammapy/blob/03f65e08ac04741ff5f1f7b1aeed20dddeac2023/gammapy/maps/wcs/ndmap.py#L680-L705)
   constructs a `RegionGeom` with the map's WCS and calls
   `geom.get_coord()`.
4. `RegionGeom.get_coord()` asks for `center_skydir`.
5. [`RegionGeom.center_skydir`](https://github.com/gammapy/gammapy/blob/03f65e08ac04741ff5f1f7b1aeed20dddeac2023/gammapy/maps/region/geom.py#L145-L221)
   returns the center of `_rectangle_bbox`.
6. A point region has a degenerate pixel bounding box. Gammapy's fallback
   creates a one-by-one `RectanglePixelRegion` and calls
   `rectangle_pix.to_sky(self.wcs)`.
7. Regions 0.12
   [`RectanglePixelRegion.to_sky()`](https://github.com/astropy/regions/blob/f6919cc882e752d788e815cb35285ca3126d5260/regions/shapes/rectangle.py#L117-L132)
   calls `pixel_shape_to_sky_svd()`.
8. Regions
   [`compute_local_wcs_jacobian()`](https://github.com/astropy/regions/blob/f6919cc882e752d788e815cb35285ca3126d5260/regions/_utils/wcs_helpers.py#L289-L381)
   converts `(x, y)`, `(x + 1, y)`, and `(x, y + 1)` to sky coordinates,
   builds a two-by-two tangent-plane forward matrix, and inverts it.
9. `pixel_shape_to_sky_svd()` multiplies the inverse Jacobian by the pixel
   rectangle's semi-axis matrix.
10. `_svd_ellipse_from_composite()` passes that composite to
    `np.linalg.svd()`, where the issue reports `err='invalid value'` and
    `LinAlgError("SVD did not converge")`.

The synthetic map is created by
[`EDispMap.from_diagonal_response()`](https://github.com/gammapy/gammapy/blob/03f65e08ac04741ff5f1f7b1aeed20dddeac2023/gammapy/irf/edisp/map.py#L245-L278)
with:

```text
npix=(2, 1)
proj="CAR"
binsz=180
```

Pinned `WcsGeom.create()` source implies `CRPIX=(1.5, 1)`,
`CRVAL=(0, 0)`, and `CDELT=(-180, +180)` for this geometry. A fixed
one-pixel y sample is therefore a 180-degree latitude step rather than a
small local perturbation.

SciPy is not on this traceback path. Astropy supplies the WCS transforms, and
NumPy surfaces the non-finite or non-convergent composite at SVD. The source
evidence does not support assigning the root cause to either library.

## Regions change history

Regions 0.11
[`RectanglePixelRegion.to_sky()`](https://github.com/astropy/regions/blob/988b2672817942796351b5d0da8e80596541f2df/regions/shapes/rectangle.py#L107-L121)
used `pixel_scale_angle_at_skycoord()` with a one-arcsecond northward sky
offset and an isotropic scale. Regions 0.12 instead maps the rectangle through
a local Jacobian and SVD.

The relevant 0.12 history is:

- [Regions PR #650](https://github.com/astropy/regions/pull/650), merged as
  [`618cf2d`](https://github.com/astropy/regions/commit/618cf2dc865aa5b493c4a0578dbeb915985e7d8e),
  introduced improved local Jacobian conversions. Its discussion moved from a
  fixed angular sample to one-pixel samples to improve stability across
  ordinary pixel scales.
- [Regions PR #651](https://github.com/astropy/regions/pull/651), merged as
  [`887f59b`](https://github.com/astropy/regions/commit/887f59b37d3f6f76a9b042140daf105b0ac8c5ec),
  extended the SVD treatment for elliptical conversions and shear.
- [Regions PR #676](https://github.com/astropy/regions/pull/676), merged as
  [`0e8fc73`](https://github.com/astropy/regions/commit/0e8fc73d18f0c5b1d795945a1a5cdc4765779bff),
  made the Jacobian pole- and longitude-wrap-safe through great-circle
  offsets and moved rectangular conversions onto the SVD path.

The relevant Regions `v0.12` and current-`main` helper blobs are identical, as
are the relevant rectangle-conversion blobs. No later source repair was found.

These changes improve general WCS conversion behavior. This dossier does not
claim that the one-pixel method is globally incorrect. It isolates an
extreme 180-degree-per-pixel CAR geometry for which a nominal one-pixel
finite difference is not a local sample.

## Evidence and execution boundary

Evidence established here:

- the public issue's exact dependency versions, traceback, and listed failing
  tests;
- pinned release, maintenance, and current source;
- the old and new Regions rectangle-conversion paths;
- the dependency-cap diffs and their maintainer comments;
- current ownership and bounded overlap searches.

Not established here:

- the numerical values of `sky_x`, `sky_y`, the forward matrix, its
  determinant or rank, the inverse Jacobian, or the SVD composite;
- whether every one of the four parameterized sky positions fails;
- whether Regions 0.11 passes every position on the same full stack;
- whether a different Astropy or NumPy version changes the earliest invalid
  value;
- whether a Gammapy-local center shortcut or a Regions-level numerical change
  is the accepted repair.

No Gammapy or Regions checkout, environment, dependency, issue attachment,
runtime reproduction, test execution, or generated science artifact was
created. Do not describe this dossier as a local reproduction.

## Unexecuted stack and position matrix

The smallest future diagnostic should preserve the distinction between
reported facts and unverified controls:

| Gammapy | Regions | Position | Current evidence | Purpose |
| --- | --- | --- | --- | --- |
| 2.1 | 0.12 | `0d 0d` | Reported failing | Smallest equatorial regression |
| 2.1 | 0.12 | `180d 0d` | Reported failing | Longitude-wrap control |
| 2.1 | 0.12 | `0d 90d` | Reported failing | North-pole control |
| 2.1 | 0.12 | `180d -90d` | Present in the parameterization but not listed among the issue's failures | South-pole control; do not assume pass or fail |
| 2.1 | 0.11 | all four positions | Not executed here | Pre-change comparison |
| current `v2.1.x` | 0.11 and 0.12 | all four positions | Not executed here | Determine maintenance-head behavior |
| current `main` | 0.12 | resolver excludes this combination | Cap-removal acceptance control only after an approved repair |

Run the 0.11 and 0.12 rows in isolated, exactly recorded environments. Change
one dependency boundary at a time. Do not infer causality from a resolver
success or failure.

## Smallest future offline regression and instrumentation

The focused regression already exists:

[`test_edisp_from_diagonal_response`](https://github.com/gammapy/gammapy/blob/03f65e08ac04741ff5f1f7b1aeed20dddeac2023/gammapy/irf/edisp/tests/test_map.py#L153-L174).

It constructs small energy axes and a synthetic diagonal EDisp map, requests a
kernel at each of four sky positions, and checks that the interior kernel rows
sum to one. It needs no `gammapy-data`, FITS fixture, network, GPU, or
observatory dataset.

The first diagnostic node should be:

```text
gammapy/irf/edisp/tests/test_map.py::test_edisp_from_diagonal_response[0d 0d]
```

Before selecting a fix, instrument a disposable diagnostic path immediately
before the Regions SVD and record, for each position:

1. `(x0, y0)` and the WCS header;
2. `sky0`, `sky_x`, and `sky_y`, including masked or non-finite components;
3. the tangent-plane forward matrix;
4. determinant, rank, and condition number when finite;
5. the inverse Jacobian and the composite matrix passed to SVD;
6. the earliest operation that creates a non-finite value.

Instrumentation is diagnostic evidence, not a proposed public logging change.
After maintainers select the contract, the committed test should assert
successful kernel construction and normalization, not the historical
`LinAlgError`.

Then run the four-position node, the EDisp map test module, and the project's
ordinary test gate. A Regions-level repair additionally needs focused
rectangle/Jacobian tests covering ordinary small pixels, distorted WCS,
longitude wrap, both poles, very coarse valid samples, and invalid-domain
offsets.

## Unresolved owner and release decisions

Three repair boundaries remain plausible:

### Gammapy point-center adaptation

For a single `PointSkyRegion`, Gammapy could use the point itself as the region
center instead of converting a one-pixel bounding rectangle to sky solely to
recover its center. This is narrow and avoids asking for meaningless rectangle
width, height, and orientation in the affected path.

Maintainers must define behavior for multiple or compound point regions and
confirm that bypassing `_rectangle_bbox` preserves all intended `RegionGeom`
semantics.

### Regions finite-difference behavior

Regions could use an adaptive or domain-aware local sample and explicitly
handle non-finite or non-invertible Jacobians. That may protect other users of
very coarse WCS geometries.

Exact celestial poles and projection-domain boundaries require an explicit
contract. A fallback must not silently invent rectangle scale or orientation
where the local transformation is not invertible.

### Dependency containment

Gammapy can retain `regions<0.12`, but that defers compatibility and leaves the
underlying boundary unresolved. Maintainers must decide:

- which repository owns the durable repair;
- whether Gammapy `v2.1.x` receives a backport or only a dependency cap;
- what acceptance evidence permits removing the cap from `main`;
- whether the Astropy and SciPy caps are independently removable;
- whether a cross-project issue should be opened before code begins.

This dossier does not select among those options.

## Ownership and overlap

At the live check:

- #6775 was open, unassigned, and had zero comments;
- it had no milestone or linked development;
- exact `6775` and `"SVD did not converge"` pull-request searches returned no
  matching Gammapy pull request;
- exact branch and commit searches returned no matching branch or commit;
- Regions issue and pull-request searches found the merged conversion work,
  but no later open repair for this 180-degree-per-pixel boundary;
- Gammapy PRs #6737 and #6748 are merged containment work, not ownership of a
  durable fix.

Bounded searches cannot prove that no work exists anywhere. Recheck issue
comments, assignment, linked development, matching pull requests, branches,
dependency constraints, and both repositories' current heads immediately
before any future contact or implementation.

## Contribution and AI policy

Gammapy's pinned
[community and AI guidelines](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/docs/development/guidelines.rst)
require a contributor to discuss an issue and proposed approach before coding.
They require disclosure of AI assistance, human understanding, authorship,
supervision, and validation, and reject copied or purely automated AI
contributions.

The pinned
[developer guide](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/docs/development/intro.rst),
[CONTRIBUTING file](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/CONTRIBUTING.md),
and
[pull-request template](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/.github/PULL_REQUEST_TEMPLATE.md)
also require a small tested change and DCO signoff with the human
contributor's real identity.

Any future discussion, implementation, and pull request must be human-led and
must disclose material AI assistance. This dossier is research input, not text
to paste upstream.

## Resource boundary

- Current artifact: source-only Markdown; negligible CPU and storage
- Focused future test: synthetic and offline; no external science data
- Diagnostic version matrix: multiple isolated scientific Python
  environments; not created in this cycle
- Full Gammapy validation: potentially larger dependency and data footprint;
  not authorized in this cycle
- GPU, HPC, credentials, cloud services, and observatory access: not required
- Workspace storage at final source audit: 99% used, about 7.9 GiB available;
  critical risk
- Capacity/provider meter: unknown; observation-only

No dependency or checkout work should begin without a fresh capacity check,
cleanup plan, and implementation-slot release.

## Decision

- Status: **waiting**
- Evidence verdict: **GO**
- Dispatch verdict: **WAIT**
- Importance: high for gamma-ray response-kernel validation and dependency
  compatibility
- Runtime reproduction: not performed
- Ownership: apparently unowned; durable repair owner is unresolved
- Ready for implementation: no
- Blockers:
  - BuildKit PR #6966 occupies the sole implementation slot;
  - Gammapy requires issue discussion before coding;
  - maintainers must choose Gammapy adaptation, Regions repair, or continued
    dependency containment;
  - the maintenance/backport and cap-removal contracts are undefined;
  - the exact non-finite matrix boundary is not locally captured;
  - workspace storage is critically constrained.
- Exact next action: preserve this dossier and observe #6775, the dependency
  caps, and both repository heads; after the implementation slot clears and
  upstream contact is authorized, revalidate ownership and ask maintainers
  which repository and release line should own the fix before creating the
  exact-version diagnostic environment.
- Resumable stopping point: the released-stack failure, cross-project call
  path, dependency containment, change history, and future offline diagnostic
  matrix are documented; no fix was selected and no upstream action occurred.
