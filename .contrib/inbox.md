# Opportunity inbox

Capture only public information. This is a durable lead log, so a row may remain after
revalidation. `.contrib/tracker.yaml` and the Observer Manager are authoritative for
current status, promotion, and dispatch; dossiers record the evidence behind a
decision.

| Project | Issue or idea | Why it matters | Reproduction clue | Size | Captured |
| --- | --- | --- | --- | --- | --- |
| BuildKit | [#4001](https://github.com/moby/buildkit/issues/4001) OTLP tracing docs | Improves production observability onboarding | Compare supported OTEL variables with docs and a local Collector | Medium | 2026-07-19 |
| Moby | [#50732](https://github.com/moby/moby/issues/50732) gotestsum retry experiment | Better CI signal and less flaky-test waste | Controlled pass/flaky/fail/race matrix | High | 2026-07-19 |
| scikit-learn | [#28793](https://github.com/scikit-learn/scikit-learn/issues/28793) `copy=False` behavior | Python/data-science entry with bounded reproduction | Test dtype and writeability combinations | Low-medium | 2026-07-19 |
| Kueue | Capacity, metrics, and diagnostics opportunity | Direct AI scheduling and SRE alignment | Review current help-wanted issues before selection | Medium-high | 2026-07-19 |
| OpenTelemetry Python Contrib | GenAI instrumentation or context propagation | Strong Python, AI, and observability overlap | Review semantic conventions and instrumentation tests | Medium | 2026-07-19 |
| OpenCost | Kubernetes cost correctness or cloud integration | Strong FinOps differentiation | Review unassigned accuracy and metrics issues | Medium | 2026-07-19 |
| Dask | [#11884](https://github.com/dask/dask/issues/11884) dataframe dtype regression | Scientific Python and data-pipeline correctness | Reproduce `.str.split` behavior against pandas and add the smallest regression test | Low-medium | 2026-07-19 |
| Apache Airflow | [#69813](https://github.com/apache/airflow/issues/69813) SSH remote-path validation | Remote execution and pipeline reliability | Map create/execute validation paths and prove inconsistent behavior | Medium | 2026-07-19 |
| Flyte | [#7448](https://github.com/flyteorg/flyte/issues/7448) DB repository Prometheus metrics | Kubernetes-native research/ML workflow observability | Confirm metrics-epic dependencies and repository instrumentation conventions | Medium | 2026-07-19 |
| Zarr Python | [#2706](https://github.com/zarr-developers/zarr-python/issues/2706) nested FSMap compatibility | Cloud scientific-data interoperability | Clarify remaining nested-filesystem scope after PR #2774 before coding | Medium | 2026-07-19 |
| Astropy | [#11148](https://github.com/astropy/astropy/issues/11148) structured-column ASCII error | Core astronomy data correctness and diagnostics | Reproduce on current main and determine support versus validation semantics | Low-medium | 2026-07-19 |
| Gammapy | [#6787](https://github.com/gammapy/gammapy/issues/6787) development-dependency CI | Gamma-ray science pipeline reliability | Inspect failed workflow matrix, dependency pins, and intended dev-deps coverage | Medium | 2026-07-19 |
| Gammapy | [#6716](https://github.com/gammapy/gammapy/issues/6716) cross-version dataset compatibility | Protects reproducibility of serialized scientific analyses | Pinned source matrix isolates markerless GADF-to-OGIP misdispatch; await mandatory issue discussion, target decision, and slot | Medium-high | 2026-07-19 |
| yt | [#2281](https://github.com/yt-project/yt/issues/2281) particle-deposition performance | Scalable astrophysical simulation analysis | Establish representative datasets and benchmark before considering code | High | 2026-07-19 |
| Bilby | [#1114](https://github.com/bilby-dev/bilby/issues/1114) BNS lambda overwrite | Can invalidate post-processing after long gravitational-wave inference | Arithmetic overwrite reproduced; define complete and partial mixed-input semantics | Medium | 2026-07-19 |
| Lightkurve | [#1531](https://github.com/lightkurve/lightkurve/issues/1531) exact TIC search returns nearby targets | Wrong-star products can contaminate TESS analysis | Source/history mapped; after slot release, recheck reporter intent and add an offline exact-identity regression | Medium | 2026-07-19 |
| Lightkurve | [#1565](https://github.com/lightkurve/lightkurve/issues/1565) nondeterministic TESS product collection | Cache state changes which camera product researchers receive | Fresh TESSCut may download multiple products but opens only the first; cache uses the first detector prefix and matching path; contributor intent is active, observe | Medium | 2026-07-19 |
| yt | [#5439](https://github.com/yt-project/yt/issues/5439) empty GIZMO particle chunks | Valid simulations fail during stellar-age analysis | Assigned reporter owns active PR #5440; observe its unresolved review and missing ordinary-CI regression, do not duplicate | Medium-high | 2026-07-19 |
| GWPy | [#1850](https://gitlab.com/gwpy/gwpy/-/work_items/1850) short-series whitening | Fundamental gravitational-wave preprocessing can fail or silently shorten its FIR | [Source algebra](dossiers/gwpy-1850.md) isolates ASD-span and tap-length boundaries; await exact reporter inputs, maintainer semantics, and slot | Medium | 2026-07-19 |
| Dask | [#12507](https://github.com/dask/dask/issues/12507) hash-seed-dependent optimized graph | Scientific pipeline graph size and build time vary by orders of magnitude | Exact 2026.7.1 matrix reproduced; PR #11899 ownership filter yields 82 invariant tasks; await triage and slot | High | 2026-07-19 |
| Gammapy | [#6775](https://github.com/gammapy/gammapy/issues/6775) dependency-sensitive SVD failures | Gamma-ray response-map validation fails on the current scientific Python stack | Reduce the WCS matrix failure and locate the Gammapy/Regions/dependency boundary | Medium-high | 2026-07-19 |
| SunPy | [#8599](https://github.com/sunpy/sunpy/issues/8599) GOES-19 CCOR map loading | Public coronagraph science products need an explicit ingestion path | `allow_errors=True` is the established opt-in; code is no-go unless maintainers request a narrow file-only auxiliary-HDU exception | Medium | 2026-07-19 |
