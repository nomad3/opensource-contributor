# Prometheus Operator PR #8645 review

- Pull request: <https://github.com/prometheus-operator/prometheus-operator/pull/8645>
- Issue: <https://github.com/prometheus-operator/prometheus-operator/issues/4940>
- Reviewed commit: `75f33f373dfefeba24091a4e861e7cded84e3a8e`
- Base checked: `d7d70ebb896b1d655c1d7d88ae11a1ce6ba5b80c`
- Review date: 2026-07-19
- Upstream communication: not posted
- Verdict: **NO-GO**

## Scope

The pull request validates Prometheus web TLS Secret and ConfigMap references
before creating the generated web configuration Secret. The core validation
does reject both missing objects and missing keys, preventing the invalid
references described in issue #4940 from reaching the Prometheus pod.

The review compared the patch with current main, traced reference tracking and
informer reads, inspected the other web-config consumers, ran focused tests and
vet, and used Claude Fable 5 as an independent adversarial reviewer.

## Blocking

### Publish the reference tracker only after TLS validation

`assetStore.RefTracker()` returns its live `map[string]struct{}`. The Prometheus
sync publishes that map through `UpdateReferenceTracker()` before
`createOrUpdateWebConfigSecret()` calls the new validation helper. Validation
then calls `GetSecretKey()` and `GetKey()`, which insert into the published map.

Informer event-handler goroutines can simultaneously call `HasRefTo()`. The
`ReconciliationTracker` mutex protects access to the outer tracker map, but not
the inner `assets.RefTracker` after `HasRefTo()` obtains it. This introduces an
unsynchronized Go map read/write and can panic the operator.

Finish all `assetStore` reads before publishing its tracker. The existing
Alertmanager ordering—provision assets, then update the reference tracker—is a
useful pattern. Add race-sensitive coverage around the ordering or tracker
ownership contract.

### Add the requested unit tests

No tests were added despite the maintainer's explicit request. A table-driven
test for `ValidateTLSAssets` should cover nil TLS, a missing Secret, a missing
key, a ConfigMap certificate, and valid references. It should establish that
the intended issue behavior remains protected independently of controller
integration.

## Important

### Complete or explicitly bound the shared-controller behavior

The helper was moved to `pkg/webconfig`, but only the Prometheus server invokes
it. Alertmanager—the controller specifically named in maintainer feedback—still
creates web config without validating referenced assets. PrometheusAgent and
ThanosRuler have the same latent invalid-mount behavior.

At minimum, wire Alertmanager in this pull request or obtain explicit maintainer
agreement that the additional controllers will be handled in follow-ups.

## Checks that passed

- Missing object names and missing keys return errors through the existing
  `StoreBuilder` accessors.
- The Prometheus reconciliation stops before creating an invalid workload.
- The branch merges with current main without a textual conflict.
- Required CI checks were green at review time.
- The patch is mechanically clean.

Local validation:

```text
go test ./pkg/webconfig/... ./pkg/prometheus/server/... ./pkg/alertmanager/... ./pkg/prometheus/agent/... ./pkg/thanos/...
pass

go vet ./pkg/webconfig/... ./pkg/prometheus/server/...
pass

git diff origin/main...HEAD --check
clean
```

## Draft upstream review

> The core validation handles both missing objects and missing keys, but I found
> an ordering problem: `UpdateReferenceTracker()` publishes the live
> `assetStore.RefTracker()` map before `createOrUpdateWebConfigSecret()` runs
> `ValidateTLSAssets()`. The validation accessors insert into that map while
> informer goroutines may read it through `HasRefTo()`, and the reconciliation
> tracker lock does not protect the inner map. Could the web-config asset reads
> finish before the tracker is published?
>
> This also still needs the unit tests requested in the earlier review, and the
> helper is not yet used by Alertmanager even though that was the reason given
> for moving it into `pkg/webconfig`.
