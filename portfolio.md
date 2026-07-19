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

## Portfolio strategy

- **Fast credibility:** verified documentation, reproducibility, tests, metrics, and CI.
- **Core specialization:** AI platform reliability and observability on Kubernetes.
- **Differentiator:** combine model-serving knowledge with SRE, security, and FinOps.
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
