# Gammapy #6716 — 2.1 GADF datasets fail to reopen on 2.0.x

## Identity

- Repository: `gammapy/gammapy`
- Issue:
  [#6716](https://github.com/gammapy/gammapy/issues/6716)
- Issue state: open, labeled `bug`, milestone `2.0.2`
- Ownership: unassigned, no linked branch or pull request, and no matching pull
  request or commit found
- Issue author: `Tobychev`
- Current `v2.0.x` commit inspected:
  [`1301b6d`](https://github.com/gammapy/gammapy/commit/1301b6db2c5f53aa7bfb37c870ca4768e13ccb5c)
- Current `v2.1.x` commit inspected:
  [`531ec55`](https://github.com/gammapy/gammapy/commit/531ec555024a17fdb6d99276e765265bc1bf13d9)
- Current `main` commit inspected:
  [`6ed4106`](https://github.com/gammapy/gammapy/commit/6ed4106cbe6b2c8b045258770d6c46f1aabe6282)
- Release commits inspected:
  `v2.0.1` at
  [`2480d0b`](https://github.com/gammapy/gammapy/commit/2480d0b8978ccf73ed2addcc1df786857f75095a)
  and `v2.1` at
  [`03f65e0`](https://github.com/gammapy/gammapy/commit/03f65e08ac04741ff5f1f7b1aeed20dddeac2023)
- Live ownership and source check:
  `2026-07-19T05:15:10Z`

## Decision boundary

This is a strong, bounded astronomy-native compatibility problem, but it is
not yet authorized for implementation.

The source evidence supports a reader-only format-detection backport to the
2.0.x maintenance line. It does **not** establish that contributors should
change the 2.0.x writer default, add a format field to dataset YAML, or absorb
the broader serialization design in
[#6522](https://github.com/gammapy/gammapy/issues/6522).

Gammapy's contribution policy requires discussion on the issue before coding.
Its
[backport guide](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/docs/development/dev_howto.rst)
documents the ordinary path as labeling a pull request for automatic
maintenance backport after it merges. The relevant detection already exists on
`main`, so a maintainer must choose the target and exact compatibility
contract.

## Scientific and operational impact

Gammapy datasets preserve gamma-ray counts, background counts, exposure,
energy dispersion, masks, geometry, and analysis metadata. A serialized
analysis written by 2.1 cannot be reopened through the normal bundle reader on
2.0.1/2.0.x when its `SpectrumDatasetOnOff` payload uses the new default GADF
representation.

The issue-reported failure is explicit rather than silent: the 2.0 reader
interprets the file as OGIP and fails because the GADF file has no `EBOUNDS`
extension. Even without silent numerical corruption, this matters for:

- reproducible reopening of archived analyses;
- rollback to a supported maintenance environment;
- collaboration between machines pinned to different supported releases;
- recovery and validation of serialized spectral-analysis products.

The repository does not currently state a general promise that newer output
must be readable by every older release. The issue's `2.0.2` milestone is
evidence that maintainers consider this a maintenance bug, but it is not by
itself approval of a particular patch.

## Source-backed compatibility matrix

| Line | `SpectrumDatasetOnOff.read()` default | No-format behavior | Writer default |
| --- | --- | --- | --- |
| `v2.0.1` / current `v2.0.x` | `"ogip"` | Every non-`"gadf"` value is sent to `OGIPDatasetReader` | `"ogip"` |
| `v2.1` / current `v2.1.x` | `None` | Detect OGIP from `SPECTRUM.HDUCLASS`; otherwise detect GADF from `COUNTS_BANDS`; reject unknown layouts | `"gadf"` |
| current `main` | `None` | Same bounded GADF/OGIP detection as 2.1 | `"gadf"` |

The 2.0.x implementation already supports explicit `format="gadf"` reads. The
missing capability is dispatch when the caller has no format marker.

Pinned source:

- [2.0.x spectrum dataset I/O](https://github.com/gammapy/gammapy/blob/1301b6db2c5f53aa7bfb37c870ca4768e13ccb5c/gammapy/datasets/spectrum.py)
- [2.1.x spectrum dataset I/O](https://github.com/gammapy/gammapy/blob/531ec555024a17fdb6d99276e765265bc1bf13d9/gammapy/datasets/spectrum.py)
- [2.0.x generic dataset bundle I/O](https://github.com/gammapy/gammapy/blob/1301b6db2c5f53aa7bfb37c870ca4768e13ccb5c/gammapy/datasets/core.py)
- [2.0.x spectrum I/O tests](https://github.com/gammapy/gammapy/blob/1301b6db2c5f53aa7bfb37c870ca4768e13ccb5c/gammapy/datasets/tests/test_spectrum.py)
- [2.1.x spectrum I/O tests](https://github.com/gammapy/gammapy/blob/531ec555024a17fdb6d99276e765265bc1bf13d9/gammapy/datasets/tests/test_spectrum.py)

The behavior entered through merged
[PR #5812](https://github.com/gammapy/gammapy/pull/5812), merge commit
[`825ad10`](https://github.com/gammapy/gammapy/commit/825ad1046f1da4282b8b5b5a3d27e502c5459d3d).
That change intentionally switched the 2.1 writer default to GADF because it
preserves masks more faithfully, and added the reader detection needed for that
new default.

## Exact call path

The failure is explained by the normal bundle serialization path:

1. `Datasets.write()` asks each dataset for `to_dict()` and writes its FITS
   payload.
2. `SpectrumDatasetOnOff.to_dict()` records `name`, `type`, and `filename`; it
   does not record `format`.
3. In 2.1, the payload is GADF by default. Its recognizable extension is
   `COUNTS_BANDS`; it has no OGIP `EBOUNDS`.
4. `Datasets.read()` loads the YAML entry, selects the registered dataset type,
   and calls `SpectrumDatasetOnOff.from_dict()`.
5. `from_dict()` calls `SpectrumDatasetOnOff.read(filename=...)` without a
   format.
6. On 2.0.x, the default `"ogip"` sends that GADF file into
   `OGIPDatasetReader`.
7. The OGIP map construction expects `EBOUNDS`, producing the issue-reported
   failure before the dataset is reconstructed.

No change to generic YAML serialization is necessary to explain or narrowly
repair this path. The 2.0.x class already knows how to read GADF once dispatch
selects it.

## Evidence and execution boundary

This cycle is intentionally source-only:

- the issue report and maintainer comment establish the observed cross-version
  failure and the intentional 2.1 GADF writer change;
- pinned release, maintenance, and main sources establish the dispatch
  mismatch;
- existing 2.0.x synthetic tests establish that the maintenance line can read
  its own explicitly written GADF payload, which is a dispatch proxy rather
  than a complete 2.1-producer compatibility test;
- existing 2.1 tests establish the two recognized layout signatures.

Pinned comparison of the
[2.0.x](https://github.com/gammapy/gammapy/blob/1301b6db2c5f53aa7bfb37c870ca4768e13ccb5c/gammapy/datasets/map.py)
and
[2.1.x](https://github.com/gammapy/gammapy/blob/531ec555024a17fdb6d99276e765265bc1bf13d9/gammapy/datasets/map.py)
`MapDataset`,
[2.0.x](https://github.com/gammapy/gammapy/blob/1301b6db2c5f53aa7bfb37c870ca4768e13ccb5c/gammapy/maps/region/ndmap.py)
and
[2.1.x](https://github.com/gammapy/gammapy/blob/531ec555024a17fdb6d99276e765265bc1bf13d9/gammapy/maps/region/ndmap.py)
`RegionNDMap`, and
[2.0.x](https://github.com/gammapy/gammapy/blob/1301b6db2c5f53aa7bfb37c870ca4768e13ccb5c/gammapy/irf/edisp/map.py)
and
[2.1.x](https://github.com/gammapy/gammapy/blob/531ec555024a17fdb6d99276e765265bc1bf13d9/gammapy/irf/edisp/map.py)
`EDispMap` serialization paths found no relevant schema change for the shared
synthetic fields. That source comparison makes the 2.0.x-generated payload a
useful proxy; it still does not replace the pinned-2.1 producer acceptance
control.

The failure was **not** executed locally. No Gammapy checkout, environment,
dependency, FITS file, or external dataset was created. Do not describe this
artifact as a runtime reproduction.

## Smallest future offline regressions

No `gammapy-data` download is needed. The smallest in-tree dispatch regression
is:

1. Reuse the existing synthetic `TestSpectrumOnOff` fixture.
2. Write its dataset explicitly as GADF.
3. Assert the generated file contains `COUNTS_BANDS` and does not contain
   `EBOUNDS`.
4. Write a markerless YAML bundle containing only `name`, `type`, and
   `filename`.
5. Call `Datasets.read(path, checksum=False)`.
6. Write the test as a successful-reconstruction assertion. Run it once against
   unmodified 2.0.x to record that it fails naturally at the reported missing
   `EBOUNDS`; do not make the old exception the committed test oracle.
7. With the accepted detection logic, require successful reconstruction and
   assert dataset type, name, counts, off-counts, exposure, safe mask, and, when
   present, energy dispersion.
8. Write an explicit OGIP dataset and prove a markerless default read still
   succeeds.
9. Preserve the 2.0.x explicit `format="ogip-sherpa"` read path with a focused
   regression.
10. Add a focused unknown or malformed layout case with an intentional error
    message.

That fixture is written by 2.0.x itself. It proves markerless dispatch and the
accepted shared-field read path, but it must not be described as a complete
cross-version acceptance test. `MapDataset` and lower map-serialization sources
changed between the maintenance lines.

Before promotion, add a separate two-environment acceptance control:

1. In an environment pinned to inspected 2.1, construct the same small
   synthetic `SpectrumDatasetOnOff`.
2. Write it through the ordinary default 2.1 `Datasets.write()` path.
3. Record the producer version and commit, YAML, FITS extension inventory, and
   checksums.
4. In the candidate 2.0.x environment, read that untouched bundle through
   `Datasets.read(..., checksum=False)`.
5. Assert the fields shared by both versions and document any newer schema
   element that 2.0.x cannot represent.

The generated file need not become a permanent binary fixture unless
maintainers prefer that test shape. It is a release-to-release acceptance
control, separate from the small deterministic in-tree regression.

The proposed exact new test node should run first, followed by:

```bash
pytest gammapy/datasets/tests/test_spectrum.py::TestSpectrumOnOff::test_datasets_read_markerless_gadf
pytest gammapy/datasets/tests/test_spectrum.py
tox -e test
```

Only after the implementation is accepted should scoped pre-commit checks run
on the changed source, test, and release-note files. Gammapy's pre-commit hooks
can rewrite files, so that is an implementation-stage mutation rather than a
reconnaissance action.

## Narrow future implementation surface

If maintainers approve the approach, the smallest plausible patch is:

- add the required FITS import and format probe to the 2.0.x
  `SpectrumDatasetOnOff.read()` path;
- recognize OGIP and GADF using the established 2.1 signatures;
- preserve the 2.0.x OGIP writer default;
- add the markerless dispatch regression above and run the separate pinned-2.1
  producer control before promotion;
- add the project-required maintenance release note.

Explicit exclusions:

- no change to the 2.0.x writer default;
- no generic `Datasets.write()` or `Datasets.read()` redesign;
- no YAML schema or format-marker migration;
- no fixture-generation framework;
- no adoption of the broader format-propagation work in #6522;
- no changes to numerical spectral analysis or model fitting.

## Compatibility and review risks

### `ogip-sherpa`

The 2.0.x reader currently sends every non-`"gadf"` value through the OGIP
reader, including documented or tolerated variants such as
`format="ogip-sherpa"`. A literal copy of the 2.1 `format is None` detection
must not accidentally reject or reinterpret that explicit variant. Preserve
the current 2.0.x behavior with a regression. This is a compatibility
requirement for the bounded maintenance patch, not a maintainer-contract
blocker; ask only if maintainers explicitly propose backporting 2.1's narrower
read-format behavior.

### Malformed OGIP metadata

The 2.1 detector inspects `SPECTRUM.HDUCLASS`. A maintenance backport should
produce a clear, intentional failure for a file with a `SPECTRUM` extension but
missing or malformed `HDUCLASS`; it should not turn the compatibility fix into
a broad FITS-recovery policy.

### Compatibility depth

Successful format dispatch does not prove every 2.1 GADF feature can be
represented by 2.0.x. The 2.0.x-generated regression should be labeled as a
dispatch proxy, and the pinned-2.1 producer control should round-trip only the
synthetic fields that both versions support. Any newer schema or mask behavior
outside that fixture must be reported as a separate compatibility boundary.

### Performance and observability

Autodetection adds a small FITS-header probe before the selected reader opens
the payload. The cost is negligible relative to dataset I/O, but the code
should close the probe deterministically and emit an explicit error for unknown
layouts. No logging, telemetry, security, or distributed-systems change is
needed.

## Ownership and overlap

At the check timestamp:

- #6716 was open and unassigned;
- the issue had one technical comment from a project member;
- no linked development, matching pull request, branch, or commit was found;
- #6522 is assigned and covers the broader format-propagation design.

Lack of assignment is not permission to start. Recheck the issue, assignee,
comments, linked development, branches, matching pull requests, and both
maintenance heads immediately before any contact or code.

## Contribution policy

Gammapy's
[community and AI guidelines](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/docs/development/guidelines.rst)
require a contributor to comment on the issue, express interest, and propose an
approach before coding; pull requests without prior discussion are generally
not accepted.

The
[developer guide](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/docs/development/intro.rst),
[CONTRIBUTING file](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/CONTRIBUTING.md),
and
[pull-request template](https://github.com/gammapy/gammapy/blob/6ed4106cbe6b2c8b045258770d6c46f1aabe6282/.github/PULL_REQUEST_TEMPLATE.md)
also require:

- a small change with a regression test;
- DCO signoff using the contributor's real identity;
- explicit disclosure of AI assistance;
- human understanding, authorship, supervision, and validation;
- no copy-pasted or purely automated AI contribution.

Any future issue comment and patch must be written and owned by the human
contributor. This dossier is research input, not text to paste upstream.

## Resource assessment

- Current artifact: source-only; negligible CPU and storage
- Focused future fixture: synthetic, offline, and a few KiB
- External science data: not required for the focused regression
- Full environment: requires the Gammapy development dependency stack; not
  installed during this cycle
- Workspace storage at final validation: 97% used, about 12.4 GiB available

## Decision

- Status: source-backed reader-dispatch reconnaissance complete
- Importance: high for reproducible gamma-ray spectral-analysis bundles
- Evidence quality: GO for the bounded diagnosis and offline regression design;
  independently adversarially reviewed
- Runtime reproduction: not performed
- Ownership: apparently unowned, but issue discussion is mandatory
- Ready for implementation: no
- Dispatch blockers:
  - BuildKit PR #6966 occupies the sole implementation slot;
  - a human must discuss the approach on #6716 before coding;
  - maintainers must choose a direct 2.0.x change or another backport path.
- Promotion gate: the pinned-2.1 producer acceptance control must pass
- Preservation requirement: keep the existing 2.0.x explicit
  `format="ogip-sherpa"` read path covered by regression
- Exact next action: observe #6716 for ownership or contract changes; after the
  implementation slot clears and the user authorizes upstream contact, a human
  should ask whether maintainers want a reader-only 2.0.x detection backport
  that preserves the OGIP writer default
- Handoff:
  [`.contrib/handoffs/gammapy-6716.md`](../handoffs/gammapy-6716.md)
- External-action gate: do not comment, claim, install, implement, push, or open
  a pull request without the applicable human authorization and slot release
