# Project portfolio

This portfolio is derived from demonstrated experience in SRE, Kubernetes, AWS/GCP/OCI,
CI/CD, infrastructure as code, observability, security, FinOps, Python, MLOps, and
production AI systems. It favors operationally important work where that background
provides useful reviewer context.

## Priority tiers

| Tier | Project | Strongest alignment | Best initial contribution shapes | Entry cost |
| --- | --- | --- | --- | --- |
| A | [KServe](https://github.com/kserve/kserve) | Kubernetes model serving, MLOps, SRE | Helm tests, config propagation, validation, diagnostics | Medium |
| A | [Kueue](https://github.com/kubernetes-sigs/kueue) | AI batch scheduling, capacity, Kubernetes | Metrics, events, docs, load tests, controller tests | Medium-high |
| A | [OpenTelemetry Python Contrib](https://github.com/open-telemetry/opentelemetry-python-contrib) | Python, observability, AIOps | Instrumentation tests, context propagation, error semantics | Medium |
| A | [BuildKit](https://github.com/moby/buildkit) | Containers, CI/CD, telemetry, supply chain | Verified docs, tracing, CI fixtures, reproducibility | Medium |
| A | [OpenCost](https://github.com/opencost/opencost) | Kubernetes FinOps and cost allocation | Accuracy tests, cloud integrations, metrics, docs | Medium |
| A | [Kubeflow Pipelines](https://github.com/kubeflow/pipelines) | Python, Kubernetes, MLOps pipelines | SDK tests, pipeline behavior, CI, docs | Medium |
| B | [Moby](https://github.com/moby/moby) | Container runtime, CI reliability | Flaky-test experiments, operational docs, test tooling | High |
| B | [MLflow](https://github.com/mlflow/mlflow) | Python MLOps, model lifecycle, full stack | Integration tests, tracking/serving fixes, docs | Medium |
| B | [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) | Kubernetes observability and SRE | CRD validation, alerting tests, upgrade behavior | Medium-high |
| B | [Argo CD](https://github.com/argoproj/argo-cd) | GitOps, recovery, delivery reliability | Reconciliation tests, CI, observability, docs | High |
| B | [Tekton Pipelines](https://github.com/tektoncd/pipeline) | Kubernetes-native CI/CD | Cancellation, timeout, tracing, and retry tests | High |
| B | [Crossplane](https://github.com/crossplane/crossplane) | IaC, control planes, multi-cloud | Reconciliation, provider lifecycle, telemetry | High |
| B | [Kyverno](https://github.com/kyverno/kyverno) | Kubernetes policy and DevSecOps | Policy tests, admission behavior, CLI/CI improvements | Medium-high |
| B | [Trivy](https://github.com/aquasecurity/trivy) | Supply-chain and cloud security | Misconfiguration tests, CI, reporting behavior | Medium-high |
| C | [SGLang](https://github.com/sgl-project/sglang) | Python AI inference infrastructure | API tests, observability, deployment and docs | High |
| C | [vLLM](https://github.com/vllm-project/vllm) | Critical LLM serving | Frontend/API tests, telemetry, CPU/platform behavior | Very high |
| C | [Ray](https://github.com/ray-project/ray) | Distributed Python and ML infrastructure | Reliability tests, observability, job/serve behavior | Very high |
| C | [Gateway API](https://github.com/kubernetes-sigs/gateway-api) | Kubernetes networking and conformance | Conformance coverage and operational documentation | High |

## Scientific research and data systems

This lane targets infrastructure that makes computational research reproducible,
scalable, and observable. It deliberately favors storage, distributed execution,
workflow reliability, and provenance over domain-specific scientific algorithms.

| Tier | Project | Research and infrastructure role | Best initial contribution shapes | Entry cost |
| --- | --- | --- | --- | --- |
| A | [Dask](https://github.com/dask/dask) | Distributed Python execution for scientific and analytics workloads | Dataframe/array correctness, diagnostics, scheduler tests, CI | Medium |
| A | [Zarr Python](https://github.com/zarr-developers/zarr-python) | Cloud-native chunked scientific data storage | fsspec compatibility, async storage tests, migration diagnostics | Medium |
| A | [Xarray](https://github.com/pydata/xarray) | Labeled multidimensional scientific data | Zarr/Dask integration tests, I/O correctness, performance evidence | Medium |
| A | [Project Jupyter](https://github.com/jupyter) | Interactive and collaborative computational research | Server reliability, kernels, authentication, observability, deployment tests | Medium-high |
| A | [Flyte](https://github.com/flyteorg/flyte) | Kubernetes-native research and ML workflows | Controller metrics, execution reliability, caching, data lineage | Medium-high |
| B | [Apache Airflow](https://github.com/apache/airflow) | Community-governed data and research orchestration | Provider bugs, deferrable operators, scheduler telemetry, integration tests | Medium-high |
| B | [Argo Workflows](https://github.com/argoproj/argo-workflows) | Kubernetes workflow engine used by research and ML platforms | Artifact handling, retries, controller behavior, metrics | High |
| B | [Snakemake](https://github.com/snakemake/snakemake) | Reproducible scientific workflow execution | Executor plugins, storage plugins, provenance, CI and docs | Medium |
| B | [Apache Arrow](https://github.com/apache/arrow) | Cross-language analytical memory and interchange layer | Python integration tests, filesystem/I/O correctness, benchmarks | High |

## Astronomy and astrophysics

Astronomy is a particularly strong specialization because modern observatories and
simulations create distributed-data, reproducibility, workflow, and reliability
problems—not only domain-algorithm problems. Initial contributions should target
data integrity and infrastructure while domain knowledge develops.

Tiers express strategic fit, not issue readiness. The Observer Manager still requires
current ownership, overlap, behavior, reproduction, resource, and capacity evidence
before any implementation is dispatched.

| Tier | Project | Astronomy role | Best initial contribution shapes | Entry cost |
| --- | --- | --- | --- | --- |
| A | [Astropy](https://github.com/astropy/astropy) | Core Python foundation for astronomy | FITS/table I/O, units, time, coordinates, regression tests | Medium |
| A | [Astroquery](https://github.com/astropy/astroquery) | Programmatic access to observatory archives and catalogs | Remote-service error handling, caching, retries, test infrastructure | Medium |
| A | [Gammapy](https://github.com/gammapy/gammapy) | Gamma-ray astronomy analysis | Dataset compatibility, numerical regressions, FITS/GADF I/O, CI | Medium-high |
| A | [SunPy](https://github.com/sunpy/sunpy) | Solar-physics data analysis | WCS/coordinate interoperability, map visualization, data-client reliability | Medium |
| A | [yt](https://github.com/yt-project/yt) | Analysis and visualization of astrophysical simulations | Large-data loading, Dask integration, memory/performance tests | High |
| A | [Lightkurve](https://github.com/lightkurve/lightkurve) | Kepler and TESS time-series analysis | Search correctness, FITS lifecycle, archive integration, deterministic downloads | Medium |
| A | [Bilby](https://github.com/bilby-dev/bilby) | Bayesian inference for gravitational-wave astronomy | Parameter conversion, sampler reliability, result serialization, numerical tests | Medium-high |
| A | [GWPy](https://gitlab.com/gwpy/gwpy) | Gravitational-wave detector data analysis | Signal-processing validation, I/O, numerical edge cases, CI | Medium |
| B | [Specutils](https://github.com/astropy/specutils) | Astronomical spectroscopy | Spectrum I/O, uncertainty propagation, fitting tests | Medium |
| B | [Photutils](https://github.com/astropy/photutils) | Source detection and astronomical photometry | Numerical edge cases, segmentation, performance and API tests | Medium |
| B | [Glue](https://github.com/glue-viz/glue) | Linked-data exploration and visualization | Large-data behavior, Jupyter integration, serialization | Medium-high |
| B | [TARDIS](https://github.com/tardis-sn/tardis) | Supernova radiative-transfer simulation | Reproducibility, atomic-data pipelines, numerical validation, CI | High |
| B | [Stingray](https://github.com/StingraySoftware/stingray) | X-ray timing and spectral-timing analysis | Statistical regressions, event I/O, simulation tests | Medium |
| B | [PyUVData](https://github.com/RadioAstronomySoftwareGroup/pyuvdata) | Radio-interferometry data formats | UV data I/O, metadata validation, file compatibility | Medium-high |
| B | [katdal](https://github.com/ska-sa/katdal) | MeerKAT visibility-data access | Dask/xarray serialization, archive access, chunking, caching | High |
| B | [LSST Science Pipelines](https://github.com/lsst) | Rubin Observatory survey processing | Pipeline execution, data access, CI, provenance, operational tooling | Very high |

### Strategic astronomy infrastructure

These projects are important but generally require more ecosystem context,
specialized services, or maintainer coordination before issue selection.

| Project | Role | Best contribution lane | Entry cost |
| --- | --- | --- | --- |
| [PyVO](https://github.com/astropy/pyvo) | Virtual Observatory protocol client | Protocol errors, service interoperability, caching, fixtures | Medium |
| [JWST calibration pipeline](https://github.com/spacetelescope/jwst) | Space-telescope calibration and reduction | Reference-data handling, pipeline reproducibility, CI, numerical regression | Very high |
| [LSDB](https://github.com/astronomy-commons/lsdb) | Distributed billion-source catalog analysis | Dask graph behavior, partitioning, spatial joins, provenance | High |
| [HATS](https://github.com/astronomy-commons/hats) | Hierarchical astronomical table format | Format validation, metadata, object storage, interoperability | High |
| [SkyPortal](https://github.com/skyportal/skyportal) | Time-domain astronomy collaboration platform | Data ingestion, broker reliability, auth, observability | High |
| [Fink](https://github.com/astrolabsoftware/fink-broker) | Community alert broker | Streaming reliability, schema evolution, provenance, monitoring | Very high |
| [RAIL](https://github.com/LSSTDESC/rail) | Survey photo-z and ML pipelines | Evaluation reproducibility, calibration, uncertainty, dataset lineage | High |

High-leverage cross-project themes include reliable access to remote archives,
FITS/Zarr interoperability, WCS correctness, reproducible workflows, Dask-backed
processing, scientific-data provenance, and observability for long-running analyses.

Projects are not promoted merely because they are astronomy-related. For example,
[RASCIL](https://gitlab.com/ska-telescope/external/rascil) is excluded because its
official repository states that development is discontinued and new issues or merge
requests will not be accepted. Rubin/LSST remains strategic, but much of its work is
coordinated through team-owned Jira rather than clean, unclaimed GitHub issues.
[LINCC TAPE](https://github.com/lincc-frameworks/tape) is also excluded because its
repository is explicitly deprecated.

## Agentic AI infrastructure

Agent-framework feature work is crowded and changes quickly. The durable
specialization is the operational substrate around agents:

- trace and metric semantics for model calls, tools, memory, and handoffs;
- sandbox and credential boundaries for tool execution;
- resumable workflow state, idempotency, retries, and cancellation;
- evaluation datasets and deterministic regression harnesses;
- Kubernetes deployment, autoscaling, cost attribution, and incident diagnostics.

Prefer foundation- or community-governed dependencies such as OpenTelemetry,
Kubernetes, Jupyter, Ray, and workflow engines. Treat company-led agent frameworks
as integration targets unless they show clear maintainer guidance, open governance,
and an unowned issue with stable expected behavior.

## Portfolio strategy

- **Fast credibility:** verified documentation, reproducibility, tests, metrics, and CI.
- **Core specialization:** AI platform reliability and observability on Kubernetes.
- **Research bridge:** make scientific storage and workflows reproducible, scalable,
  observable, and cost-aware.
- **Differentiator:** combine model-serving knowledge with SRE, security, data
  engineering, scientific Python, and FinOps.
- **Long-term ownership:** adopt a subsystem or recurring operational concern after
  several accepted contributions.

Popularity is not the ranking criterion. A smaller project with responsive maintainers,
clear tests, and an unowned operational gap is usually a better use of limited capacity
than a crowded high-star repository.

## Revalidation checklist

Before work begins:

1. Read `CONTRIBUTING.md`, `SECURITY.md`, architecture docs, and relevant AI policies.
2. Confirm activity, license, supported branches, and local validation requirements.
3. Check the issue, assignee, timeline, linked pull requests, and recent related merges.
4. Identify required hardware, cloud accounts, clusters, or credentials.
5. Define the smallest acceptable artifact and a resumable stopping point.
