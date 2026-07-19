# Research, agentic infrastructure, and data-pipeline candidate scan

## Objective

Extend the contribution portfolio into scientific research infrastructure,
agent operations, DevOps, and data pipelines without duplicating active work or
competing with an assigned contributor.

Checked: 2026-07-19.

## Recommended sequence

1. Start with a bounded scientific Python or workflow reliability regression.
2. Follow with workflow observability in a Kubernetes-native project.
3. Build toward agentic infrastructure through telemetry, sandboxing, resumability,
   and evaluation rather than fast-moving framework features.

## Current candidates

| Priority | Project | Candidate | Why it fits | Initial status |
| --- | --- | --- | --- | --- |
| 1 | Dask | [#11884 — `.str.split` coerces dtype to object](https://github.com/dask/dask/issues/11884) | Recent, unassigned dataframe correctness bug with a likely bounded regression test; direct scientific Python/data-pipeline relevance. | Reconnaissance candidate |
| 2 | Apache Airflow | [#69813 — inconsistent `remote_base_dir` validation](https://github.com/apache/airflow/issues/69813) | Recent, unassigned SSH provider bug; strong pipeline reliability and remote-execution fit. | Reconnaissance candidate |
| 3 | Flyte | [#7448 — instrument runs-service DB repository layer](https://github.com/flyteorg/flyte/issues/7448) | Unassigned Prometheus instrumentation for a Kubernetes-native ML/research workflow engine. | Ask for coordination within the metrics epic before implementation |
| 4 | Flyte | [#7446 — add metrics endpoint and initialize scope](https://github.com/flyteorg/flyte/issues/7446) | Foundational observability work, but likely coupled to the broader Flyte v2 metrics plan. | Design/overlap check required |
| 5 | Zarr Python | [#2706 — FSMap compatibility](https://github.com/zarr-developers/zarr-python/issues/2706) | Important cloud scientific-data interoperability problem with clear user impact. | Do not start yet; PR #2774 solved common filesystems and remaining nested-filesystem scope needs clarification |

## Agentic infrastructure direction

No agent-framework issue was promoted from this scan. A broad AutoGen accessibility
request was open, but it is a large product feature rather than a bounded
infrastructure contribution. The stronger near-term lane is:

- OpenTelemetry GenAI semantic conventions and instrumentation tests;
- durable execution and cancellation in Flyte, Airflow, Argo Workflows, or Ray;
- sandbox, secret, and network-policy hardening around agent tool execution;
- reproducible eval and replay tooling backed by scientific data formats;
- cost, latency, and failure telemetry for multi-agent workflows.

## Promotion gates

Before moving any candidate into the active tracker:

1. Read repository contribution, security, and AI-use policies.
2. Recheck assignees, linked pull requests, recent commits, and issue discussion.
3. Reproduce the behavior on current main.
4. Identify the smallest failing regression test or evidence artifact.
5. Ask maintainers before taking work inside a coordinated epic.
6. Keep the existing one-active-implementation rule.

## Decision

- Status: candidate pool only
- Best first reconnaissance: Dask #11884
- Best infrastructure follow-up: Airflow #69813
- Best strategic ownership lane: Flyte workflow observability
- No upstream issue was claimed or commented on during this scan
