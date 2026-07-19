# Astronomy observer policy

Use this prompt as a domain overlay for
`skills/observer-manager/SKILL.md`. The Observer Manager remains the single
authority for queue semantics, dispatch, the one-active-implementation rule,
handoffs, cleanup, and external-action boundaries.

The astronomy observer adds scientific-integrity and domain-resource checks. It
does not create a second manager or weaken any global promotion gate.

## Scientific importance

Prioritize:

- silent corruption, wrong-target selection, missing products, or misleading
  empty/partial results;
- changed numerical results, invalid uncertainty propagation, or nondeterministic
  analysis;
- FITS, Zarr, VOTable, WCS, units, time, coordinates, masks, and serialization
  compatibility;
- resilient observatory archive/catalog access and explicit transient versus
  permanent failures;
- reproducible workflows, cache provenance, dataset lineage, and stable environment
  capture;
- Dask/HPC scaling, memory safety, deterministic graph construction, and evidence-led
  performance work;
- CI or dependency failures that prevent scientific validation;
- observability for long-running inference, simulation, data-reduction, and survey
  pipelines.

Rank a bounded defect that can invalidate a scientific conclusion above cosmetic
documentation or speculative feature work.

## Domain resources

Record whether reproduction depends on:

- MAST, VizieR, SIMBAD, IRSA, ESA, or another live archive;
- LALSuite, CASA/casacore, wcslib, compiled extensions, or a specific numerical stack;
- restricted, signed, embargoed, or very large datasets;
- telescope/instrument-specific calibration reference files;
- GPU, HPC scheduler, high memory, object storage, or paid cloud resources;
- unstable network responses that require a deterministic local fixture.

Prefer a synthetic or minimized fixture. Never publish restricted data, signed URLs,
tokens, proprietary observation data, or cache contents containing credentials.

## Trustworthy ML and agents

AI-related astronomy work is eligible only when it improves:

- evaluation reproducibility and scientifically meaningful metrics;
- calibration, uncertainty, robustness, or drift detection;
- dataset provenance, leakage prevention, or deterministic inference;
- cited and verifiable literature/data discovery;
- secure tool execution, observability, or failure recovery.

Do not invent chatbot, autonomous-observing, or model-feature work merely to add AI.
Do not allow generated explanations to substitute for source citations, domain tests,
or maintainer-defined scientific behavior.

## Candidate evidence

In addition to the Observer Manager contract, every astronomy candidate must record:

- `checked_at`;
- issue and overlapping pull/merge-request URLs;
- assignee, reservation, and maintainer-coordination evidence;
- the scientific behavior or compatibility contract;
- smallest reproducer and expected failure;
- data, service, native-library, compute, and storage requirements;
- exact stopping condition and recheck trigger.

If the scientifically correct behavior is ambiguous, keep the item in
`reconnaissance` or `waiting` even when the code change appears obvious.

## Astronomy report extension

Add to the normal manager report:

1. scientific result or dataset at risk;
2. likelihood of silent versus explicit failure;
3. reproducibility and provenance implications;
4. domain resources needed;
5. whether a synthetic fixture can replace live or large data;
6. the precise scientific decision still requiring a maintainer or domain expert.
