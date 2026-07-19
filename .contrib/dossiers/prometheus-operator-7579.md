# Prometheus Operator issue #7579 dossier

- Issue: <https://github.com/prometheus-operator/prometheus-operator/issues/7579>
- Repository commit: `d7d70ebb896b1d655c1d7d88ae11a1ce6ba5b80c`
- Evidence checked: 2026-07-19T03:02:20Z
- Upstream communication: not posted
- Recommendation: **NEEDS CLARIFICATION — no code patch justified**
- Independent cross-review: **GO after correcting the initial obsolete classification**

## Reported behavior

The reporter added a finalizer to a Prometheus custom resource, deleted the
resource, and expected `ResourceReconciler.OnDelete()` or the Prometheus sync's
`DeletionInProgress()` branch to log activity.

The report does not identify the added finalizer. That detail changes the
expected behavior.

## Kubernetes and controller behavior

A resource with finalizers is not deleted immediately. The API server first
sets `metadata.deletionTimestamp`, which reaches an informer as an update. The
delete event occurs only after every finalizer is removed and the object leaves
storage.

Prometheus Operator intentionally queues that deletion update only when the
resource contains its own finalizer:

```text
monitoring.coreos.com/status-cleanup
```

`ResourceReconciler.OnUpdate()` returns early when deletion is in progress and
that finalizer is absent. An arbitrary user-added finalizer therefore does not
create cleanup work for this controller.

When the `StatusForConfigurationResources` feature is enabled, the Prometheus
controller adds its status-cleanup finalizer. On deletion, the update is queued,
the controller removes configuration-resource status bindings, removes its
finalizer, and lets Kubernetes finish deletion.

## Related upstream work

The issue was opened on 2025-06-02. The same contributor subsequently authored
PR #7584, merged as `daca5fd3a83599198117fc8f7a021e0b16efaaf2` on
2025-06-17:

<https://github.com/prometheus-operator/prometheus-operator/pull/7584>

That pull request:

- added the status-cleanup finalizer for Prometheus when the status feature is
  enabled;
- changed the update predicate so deletion updates with that finalizer are
  reconciled;
- added `testFinalizerWhenStatusForConfigResourcesEnabled`, which creates a
  Prometheus resource, verifies a finalizer exists, deletes it, and waits until
  it is gone.

PR #7584 explicitly closes issue #7583, not #7579. PR #7617 explicitly closes
#7608 and only refactors the predicate helper. Neither pull request claims to
resolve arbitrary-finalizer behavior or issue #7579.

The reporter also responded to a maintainer on 2025-06-11 that #7579 should
remain open because `OnDelete` still did not run. Current main retains the
operator-owned finalizer path, but that does not establish what the reporter
expected from an unspecified finalizer.

## Ownership and overlap

- Issue #7579 is open and unassigned.
- No pull request explicitly links or mentions #7579.
- PR #7584 implements the operator-owned status-cleanup case and was authored
  by the issue reporter.
- It does not establish that #7579 is fixed because the reported finalizer and
  controller remain unspecified.
- Creating a patch now would be speculative; the required behavior is unclear.

The issue body says Prometheus, while a follow-up log excerpt shows the
PrometheusAgent controller. Current main has finalizer synchronization for both,
but the distinction matters for reproduction and historical version analysis.

## Validation

Source inspection:

```text
pkg/operator/resource_reconciler.go
  OnUpdate checks HasStatusCleanupFinalizer before ignoring deletion.

pkg/prometheus/server/operator.go
  sync invokes FinalizerSyncer before returning on deletion.

pkg/operator/finalizer.go
  FinalizerSyncer adds, cleans up, and removes the status-cleanup finalizer.

test/e2e/status_subresource_test.go
  testFinalizerWhenStatusForConfigResourcesEnabled covers deletion to gone.
```

Focused current-main tests:

```text
go test ./pkg/operator ./pkg/prometheus/server
ok github.com/prometheus-operator/prometheus-operator/pkg/operator
ok github.com/prometheus-operator/prometheus-operator/pkg/prometheus/server
```

The end-to-end test was inspected but not rerun locally because it requires the
project's gated-feature cluster suite. It verifies only that the finalizer list
is non-empty, not that the exact status-cleanup finalizer is present, and covers
Prometheus rather than PrometheusAgent.

## Smallest useful upstream action

No code change is justified without a current reproduction. A concise
maintainer-facing question should explain that:

1. `OnDelete()` is not expected while any finalizer keeps the object present;
2. current main reconciles deletion updates carrying the operator's
   status-cleanup finalizer;
3. the report needs the exact finalizer, controller, feature-gate state, and
   current-main reproduction result.

If deletion with `monitoring.coreos.com/status-cleanup` still fails on current
main, the next artifact should be a focused Prometheus or PrometheusAgent
reproducer. If the only expectation is that `OnDelete()` fires while an
arbitrary finalizer remains, the issue is based on incorrect informer semantics
and can be closed without code.

## Draft upstream comment

> `OnDelete` is not expected until all finalizers are removed and the object
> actually leaves the API. Current main does queue deletion updates carrying
> the operator's `monitoring.coreos.com/status-cleanup` finalizer, and #7584
> added an end-to-end Prometheus deletion case. Could you confirm the exact
> finalizer you added, whether this was Prometheus or PrometheusAgent, whether
> `StatusForConfigurationResources` was enabled, and whether it still
> reproduces on current main? That will distinguish an operator cleanup bug
> from the expected behavior of an arbitrary finalizer.
