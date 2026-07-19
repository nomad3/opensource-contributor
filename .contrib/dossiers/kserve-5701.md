# Dossier: KServe #5701 — WVA/EPP dispatch-metric incompatibility

- Issue: <https://github.com/kserve/kserve/issues/5701>
- Reconnaissance date: 2026-07-19
- Ownership: open, unassigned, no overlapping pull request found
- Capacity class: medium investigation; high integration validation
- Recommended state: **WAITING — version-matrix validation before code**
- Upstream communication: none

## Executive finding

The reporter's updated diagnosis is supported by source and release evidence.
This is not primarily a KServe reconciliation bug and not the originally
suspected `-rank-0` normalization bug. It is a component compatibility failure:

- KServe v0.18.0 and v0.19.0 deploy
  `llm-d-inference-scheduler:v0.7.1`;
- KServe v0.18.0 deploys WVA v0.6.0 and v0.19.0 deploys WVA v0.7.0;
- WVA v0.6.0 and v0.7.0 use the same relevant dispatch query, selecting
  `inference_extension_scheduler_attempts_total` using
  `target_model_name`, `model_name`, and `pod_name`;
- the reporter's raw v0.7.1 EPP series contains none of those labels, so both
  PromQL branches necessarily return no series;
- WVA then lacks per-replica arrival rate and enters saturation-only behavior,
  continuously recommending one replica despite high KV-cache load.

KServe v0.19.0 does **not** resolve the version skew: it retains scheduler
v0.7.1 and a WVA version with the same relevant query contract as v0.18.0.
KServe master (prepared as v0.20.0-rc0) upgrades the stack to llm-d router
v0.9.0 and WVA v0.8.0. A populated v0.9.0 router fixture exposes the deprecated
metric with `namespace`, `pod_name`, `port`, `status`, and
`target_model_name`, while WVA v0.8.0 groups by `pod_name`, `port`, and
`namespace`. That pairing is source-compatible for the reporter's first
PromQL branch.

This establishes a strong upgrade hypothesis, not a runtime proof. Before
closing #5701 or writing compatibility code, the exact v0.20 stack must be
validated under real routed load.

## Corrected problem statement

### Expected

For each successful EPP dispatch, WVA can associate the counter series with:

1. the target model;
2. the selected backend pod/instance; and
3. the namespace.

Its rate query then contributes arrival-rate observations to the queueing
model, allowing WVA to scale above the minimum under load.

### Observed on KServe v0.18.0

The reporter captured:

```text
inference_extension_scheduler_attempts_total{
  container="main",
  endpoint="9090",
  instance="…:9090",
  job="…/scheduler-metrics",
  namespace="llm-d-optimized-baseline",
  pod="…-router-scheduler-…",
  status="success"
} 10314
```

The series has no `target_model_name`, `model_name`, `pod_name`, or backend
`port`. The materially identical WVA v0.6.0/v0.7.0 queries filter on missing
model labels, so the query returns zero series before grouping can help.

The original `model_server_pod="-rank-0"` observation belongs to
`inference_pool_per_pod_queue_size`, not the dispatch counter used by WVA's
arrival-rate query. It is adjacent evidence but not the causal defect described
by the updated report.

## Version matrix

| KServe surface | Router/EPP | WVA | Static compatibility finding |
| --- | --- | --- | --- |
| v0.18.0 | `llm-d-inference-scheduler:v0.7.1` | v0.6.0 | Reporter's observed deployment lacks required dispatch labels |
| v0.19.0 | `llm-d-inference-scheduler:v0.7.1` | v0.7.0 | Same scheduler and relevant WVA query contract; version pins do not establish a fix |
| master / v0.20.0-rc0 | `llm-d-router-endpoint-picker:v0.9.0` | v0.8.0 | Source/fixture labels match WVA query; runtime proof pending |

## Source contract

WVA v0.6.0 and v0.7.0 use this materially identical query:

```promql
sum by (pod_name, namespace) (
  rate(inference_extension_scheduler_attempts_total{
    status="success",
    namespace="<namespace>",
    target_model_name="<model>"
  }[1m])
)
or
sum by (pod_name, namespace) (
  rate(inference_extension_scheduler_attempts_total{
    status="success",
    namespace="<namespace>",
    model_name="<model>",
    target_model_name=""
  }[1m])
)
```

WVA v0.8.0 adds `port` to the grouping key but retains the same model-label
contract. The llm-d router v0.9.0 metric fixture includes:

```text
inference_extension_scheduler_attempts_total{
  namespace="ns-1",
  pod_name="pod-1",
  port="8080",
  status="success",
  target_model_name="modelA"
} 2
```

The metric is marked deprecated in favor of
`llm_d_epp_scheduler_attempts_total`, so future work must also track the
consumer's migration before the compatibility alias is removed.

## Existing related work

- WVA issue #1056 and merged PR #1058 fixed the consumer-side lookup to prefer
  `pod_name` over the Prometheus scrape-target `pod` label and corrected the ITL
  metric name.
- WVA issue #1072 tracks a broader redesign away from repeated pod-name and
  ownership traversal. It is assigned and has substantial design discussion.
- WVA v0.8.0 contains newer instance/variant attribution work, including PRs
  #1121 and #1145.
- No KServe PR references #5701 as of reconnaissance time.

These changes improve attribution after the required labels exist; they cannot
make a PromQL selector match a v0.7.1 series that lacks the selected labels.

## Smallest useful validation

Use a disposable cluster with the KServe v0.20.0-rc0 dependency versions.
Do not test by hitting the workload Service directly; route sustained requests
through the gateway/EPP.

Capture:

```promql
inference_extension_scheduler_attempts_total{status="success"}
```

and, if present:

```promql
llm_d_epp_scheduler_attempts_total{status="success"}
```

Then verify:

1. successful series contain `namespace`, `pod_name`, `port`, and
   `target_model_name` (or the WVA query's documented fallback labels);
2. WVA's exact dispatch-rate query returns one series per backend instance;
3. the series joins with vLLM metrics for the same replicas;
4. `wva_desired_replicas` rises above `minReplicas` under sustained load;
5. removing load eventually produces a controlled scale-down;
6. logs no longer report “vLLM metrics but no dispatch rate”.

Record all component image digests, not only mutable tags.

## Decision tree

- **If v0.20.0-rc0 works:** prepare a KServe #5701 issue comment with the exact
  compatible version matrix and recommend upgrading; separately decide whether
  KServe v0.18/v0.19 documentation needs a known-issue warning.
- **If router v0.9.0 emits correct labels but WVA still returns no data:** move
  the bug to `llm-d/llm-d-workload-variant-autoscaler` with the exact query,
  raw series, and join diagnostics.
- **If router v0.9.0 lacks labels under the real configuration:** file against
  `llm-d/llm-d-router`, including the EPP config and both deprecated/new metric
  series.
- **If only KServe-generated monitoring configuration drops labels:** retain
  ownership in KServe and patch its PodMonitor/ServiceMonitor relabeling.

## Risks and unanswered questions

- The v0.9.0 fixture proves exposition shape in a test scenario, not that the
  KServe-generated EPP configuration populates non-empty backend identity
  labels in production.
- The new `llm_d_epp_*` metric namespace may make compatibility temporary if
  WVA continues querying only the deprecated name.
- The reporter's saturation-only decision of one replica despite high
  KV-cache warrants independent confirmation; arrival-rate loss is proven, but
  the fallback policy may have changed in WVA v0.8.0.
- A full GPU-backed validation is expensive. A simulator is acceptable only if
  it exercises real EPP label production and WVA PromQL, not synthetic metrics
  that pre-populate the expected labels.

## Exact next action

Do not implement against KServe v0.18/v0.19. First run the six-step validation
against the pinned v0.20.0-rc0 component matrix. Preserve the resulting raw
Prometheus series, WVA query output, scaling decisions, and image digests in a
handoff. Only then select the owning repository and smallest patch or
documentation change.
