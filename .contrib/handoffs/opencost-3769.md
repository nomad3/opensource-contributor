# Handoff: OpenCost #3769

## Objective

Make custom-provider spot identity agree with the spot prices already selected
from Kubernetes labels, so `kubecost_node_is_spot` and allocation pricing do
not silently use on-demand classification.

## Completed

- Confirmed the issue is open, unassigned, and has no identified overlapping
  pull request.
- Read the repository's root `AGENTS.md`.
- Traced custom label lookup, node pricing, `models.Node.IsSpot()`, exporter
  metrics, and allocation's `QueryNodeIsSpot` path.
- Added a focused test in a disposable checkout.
- Confirmed the test fails only because `IsSpot()` is false while the spot CPU
  price is already selected.
- Stopped before production code when Observer Manager enforced the single
  implementation slot.

## Evidence

- Base revision: `86698e97505ea9803d71c06e91a958a58645ee57`
- Command:
  `go test ./pkg/cloud/provider -run '^TestCustomProviderNodePricingReportsSpotUsage$' -count=1`
- Result: expected failure at `IsSpot() = false`; package completed in 1.203s.
- Failing-test patch:
  `.contrib/patches/opencost-3769-failing-test.patch`
- Disposable checkout at artifact capture:
  `upstreams/opencost-3769`, branch
  `fix/custom-provider-spot-usage-type`, dirty only with the exported test.
  It is safe to delete after verifying the patch artifact.

## Current diff

No production diff. The saved patch adds one regression test to
`pkg/cloud/provider/provider_test.go`.

## Next exact action

After the implementation slot clears:

```bash
git apply /path/to/opensource-contributor/.contrib/patches/opencost-3769-failing-test.patch
go test ./pkg/cloud/provider -run '^TestCustomProviderNodePricingReportsSpotUsage$' -count=1
```

Then capture `usageType := key.Features()` before pricing fallback, use a
separate lookup key for price fallback, and return the original `usageType` on
the node. Add fallback and non-spot cases that assert exact `UsageType`,
`IsSpot()`, CPU price, and RAM price, then run the validation listed in the
dossier.

## Risks or unanswered questions

- Preserve spot identity even when pricing falls back.
- Confirm maintainers accept the existing feature value (`default,spot`) as
  `UsageType`; this is the minimal value already produced by the custom
  provider and is accepted by `IsSpot()`.
- Recheck whether a contributor or PR claims the issue.

## Do not do

- Do not sanitize the Kubernetes label map.
- Do not change Prometheus queries.
- Do not update dependencies.
- Do not expand or adjust the saved test while the implementation slot is
  occupied.
- Do not open another implementation while BuildKit #6966 remains active
  unless the user explicitly overrides that policy.
