# OpenCost #3769 dossier

## Decision

**WAITING — root cause reproduced, but BuildKit #6966 occupies the single
implementation slot.**

The issue is open and unassigned. No linked or searchable overlapping pull
request was found. The user authorized execution when confidence was high, so a
focused regression test was added in a disposable checkout and run before any
production edit. It failed for the expected reason.

Observer Manager then enforced `implementation_limit: 1`: BuildKit PR #6966 is
still the authoritative active implementation. Work stopped with no OpenCost
production change, commit, push, comment, or pull request.

Creating the failing test was itself implementation work, so dispatch should
have been rejected before that edit. This was a control-plane breach, even
though it stopped before production code. The saved test is retained as a
handoff artifact; no expansion, adjustment, or production implementation is
authorized until the slot clears or the user explicitly overrides the global
limit.

## Upstream state

- Project: `opencost/opencost`
- Issue: [#3769 — Spot pricing not applied in allocation API](https://github.com/opencost/opencost/issues/3769)
- Evidence refreshed: 2026-07-19T03:28:49Z
- Base branch: `develop`
- Revision inspected: `86698e97505ea9803d71c06e91a958a58645ee57`
- Assignees: none
- Linked closing PRs: none
- Open PR search for issue number and reported metric: no overlap found

## Reported impact

With the custom provider and a configured spot-node label:

- `node_cpu_hourly_cost` uses the configured spot price;
- `kubecost_node_is_spot` reports `0`; and
- allocation endpoints apply the base price instead of the spot price.

This is a cost-correctness defect: exporter pricing and allocation pricing
diverge for the same node.

## Root cause

The initial issue discussion suspected Prometheus label-name sanitization.
Current source contradicts that hypothesis:

1. `CustomProvider.GetKey()` receives the original Kubernetes label map.
2. `customProviderKey.Features()` correctly returns `default,spot` when
   `opencost.node-type=worker`.
3. `CustomProvider.NodePricing()` therefore selects the configured spot CPU and
   RAM prices.
4. The returned `models.Node` never receives `UsageType`.
5. `models.Node.IsSpot()` only checks whether `UsageType` contains `spot` or
   `emptible`, so it always returns false for custom-provider nodes.
6. The metric exporter writes `kubecost_node_is_spot` from `node.IsSpot()`.
   Allocation later consumes that metric and applies base rates.

The failing test proves the divergence directly: the spot CPU-price assertion
passes, while `node.IsSpot()` is false.

## Test-first evidence

Command:

```bash
go test ./pkg/cloud/provider -run '^TestCustomProviderNodePricingReportsSpotUsage$' -count=1
```

Result:

```text
--- FAIL: TestCustomProviderNodePricingReportsSpotUsage (0.00s)
    provider_test.go:239: IsSpot() = false, want true for custom spot label
FAIL
FAIL    github.com/opencost/opencost/pkg/cloud/provider    1.203s
```

Saved patch:

- `.contrib/patches/opencost-3769-failing-test.patch`

## Smallest production change after dispatch

Capture `usageType := key.Features()` before pricing fallback, use a separate
lookup key for fallback, and return `models.Node{UsageType: usageType, ...}`.
Do not change label handling or the downstream metric query.
The implementation must define fallback semantics explicitly:

- a label-classified spot node should remain identified as spot even if spot
  pricing is unavailable and price lookup falls back to `default`; and
- an ordinary node should remain non-spot.

The exact local variable used for pricing lookup should not accidentally erase
the node's classification when it falls back.

## Required validation

1. Apply the saved failing-test patch.
2. Re-run the focused test and confirm the expected failure.
3. Add the minimal `UsageType` propagation.
4. Add or extend table cases for:
   - matching dotted Kubernetes label;
   - non-matching value;
   - missing label;
   - spot classification with missing spot-price entry.
5. Assert the exact `UsageType` (`default,spot` or `default`) as well as
   `IsSpot()`, CPU price, and RAM price.
6. Run focused validation first:

```bash
go test ./pkg/cloud/provider -count=1
go test ./pkg/costmodel -count=1
go test ./pkg/cloud/... -count=1
```

7. Run the repository-required full gates before committing:

```bash
go fmt ./...
git diff --check
go vet ./...
just test
```

The metric-path test should demonstrate that `models.Node.IsSpot()` produces
the value consumed by `kubecost_node_is_spot`. If disk, time, platform, or
external-service constraints prevent a full gate locally, stop at a documented
handoff with the focused results and the exact pending command. Do not publish
or promote the upstream PR until the full gate passes on an appropriate runner
or upstream CI.

## Risks

- Setting `UsageType` from the post-fallback pricing key could incorrectly
  classify a spot node as on-demand.
- Changing label sanitization would be unnecessary and could break valid
  Kubernetes label lookup.
- Custom-provider users may observe corrected, higher or lower allocation
  totals; this is the intended user-visible effect and needs release notes.

## Resume gate

Resume any implementation work—including test expansion—only when BuildKit
#6966 no longer occupies the implementation slot or the user explicitly
overrides the one-slot control-plane policy. Recheck issue ownership and
overlapping PRs immediately before applying the saved test.
