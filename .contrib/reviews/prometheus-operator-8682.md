# Maintainer review: Prometheus Operator PR #8682

- Pull request: <https://github.com/prometheus-operator/prometheus-operator/pull/8682>
- Issue: <https://github.com/prometheus-operator/prometheus-operator/issues/8681>
- Reviewed head: `b949fb744c6a4cf67fb85dc5a35586ce93465d8b`
- Review date: 2026-07-19
- Mode: read-only; no upstream comment, review, commit, or branch mutation
- Verdict: **DO NOT PROMOTE**

## Scope and operational importance

The issue reports a high-impact failure: Prometheus 3.11 ignores a non-primary
EndpointSlice for a Service admitted with `PreferDualStack` or
`RequireDualStack`. Prometheus Operator currently emits only the first
preferred node address, so an IPv6-primary dual-stack Service can receive only
an IPv4 kubelet EndpointSlice and lose all kubelet scrape targets.

That exact production chain still needs the admitted Service object as
evidence. Prometheus's `nonPrimaryIPFamilySlice()` does not filter when
`Service.Spec.IPFamilyPolicy` is nil or single-stack, while the issue's
rendered manifest omits the policy and describes `IPFamilies: [IPv6]`. The
patch's duplicate-target regressions below are independently demonstrable and
do not depend on resolving that environment-specific discrepancy.

The pull request changes node discovery from one preferred address per node to
all addresses of the preferred Kubernetes address type. That produces the
missing IPv6 input needed by the existing EndpointSlice partitioning logic.

## Findings

### BLOCKING

1. **The shared address expansion changes the legacy `Endpoints` contract and
   creates duplicate kubelet targets for a dual-stack node.**

   `sync()` passes the same expanded `addresses` slice to both
   `syncEndpoints()` and `syncEndpointSlice()`. For a node with IPv4 and IPv6
   `InternalIP` values, the patch therefore writes two `EndpointAddress`
   entries with the same Node `TargetRef` into the legacy `v1.Endpoints`
   object.

   Prometheus's `role: endpoints` discovery creates a target for every
   `EndpointAddress` and port; it does not collapse addresses that refer to the
   same Node. Users retaining the deprecated but supported Endpoints role would
   therefore scrape both addresses for each dual-stack node. This is a behavior
   regression from the current one-address-per-node contract and was already
   identified as a caveat by the issue author.

   This matters even when the operator manages both resources: the controller
   options independently enable `Endpoints` and `EndpointSlice`, and the issue
   reproducer itself runs with both management flags enabled. The fix should
   preserve one selected address per node for `syncEndpoints()` while providing
   one address per family to `syncEndpointSlice()`, or otherwise establish an
   explicit migration contract.

2. **Returning every preferred-type address is broader than “one address per
   family” and can duplicate targets within a single family.**

   The old implementation deliberately used `addresses[0]`, mirroring
   Prometheus node discovery. The new `nodeAddresses()` returns the entire
   `NodeInternalIP` or `NodeExternalIP` slice. Kubernetes does not make this
   helper's implicit invariant—at most one address of each family—part of the
   function contract.

   A node reporting two IPv4 `InternalIP` values now becomes two IPv4
   EndpointSlice endpoints and two legacy Endpoint addresses, even though the
   bug only requires retaining the first IPv4 and first IPv6 address. The tests
   cover one address per family but no repeated same-family input, so this
   expansion is unguarded.

   Select at most one valid address per IP family while preserving node address
   order, and add a regression case with two same-family addresses.

### IMPORTANT

1. **The controller-level test does not exercise a dual-stack node.**

   `TestGetNodeAddresses` proves that both addresses enter the intermediate
   slice. `TestSync` proves EndpointSlice partitioning only with separate
   single-address IPv4 and IPv6 nodes. It does not construct one node with both
   `InternalIP` families and assert:

   - one IPv4 and one IPv6 EndpointSlice endpoint;
   - the intended legacy Endpoints behavior;
   - stable cleanup when one family disappears.

   A controller-level regression test is the clearest protection for the
   cross-resource behavior at issue.

2. **Promotion still requires maintainer approval.**

   All visible build, lint, unit, extended, generation, and E2E checks are
   green on the reviewed head, and the PR is mergeable. GitHub nevertheless
   reports `REVIEW_REQUIRED` and `mergeStateStatus: BLOCKED`. The author has
   addressed the maintainer's mechanical review requests, but no approval is
   recorded.

### OPTIONAL

1. Document whether the intended release note covers only
   `serviceDiscoveryRole: EndpointSlice` or also promises safe behavior for
   users that still enable the legacy Endpoints path.

## Positive assessment

- The missing per-family EndpointSlice input is real; the reported
  Prometheus-filtering chain is plausible for an admitted dual-stack Service
  but requires the live Service policy to prove.
- Address priority and InternalIP/ExternalIP fallback behavior are preserved.
- Invalid IPs continue to be reported and skipped rather than emitted.
- IPv4/IPv6 classification uses `net.ParseIP` and `To4`, matching the existing
  EndpointSlice partitioning model.
- Unit coverage exercises internal/external preference, fallback, no-address
  errors, and the basic dual-stack case.
- The current head passes the repository's substantive CI matrix.
- Changes remain confined to the kubelet controller and its tests.

## Evidence inspected

- Complete PR patch and seven-commit sequence
- Issue #8681 description, root-cause analysis, workaround, and caveat
- Current `sync`, `syncEndpoints`, `syncEndpointSlice`, and `nodeAddresses`
  implementations
- Current and base node-address selection behavior
- Controller and helper tests at the reviewed head
- Maintainer review discussion and author responses
- Prometheus `discovery/kubernetes/endpoints.go`, where each
  `EndpointAddress`/port pair is appended as a discovery target
- PR merge state, review decision, and complete visible check matrix

## Smallest acceptable revision

Keep the new per-family discovery needed by EndpointSlice, but do not pass that
unfiltered expansion into the legacy Endpoints writer. Establish explicit
selection functions for:

1. one preferred address per node for legacy Endpoints; and
2. at most one preferred address per IP family per node for EndpointSlice.

Add a controller test with a single dual-stack node and a helper test with
duplicate same-family addresses. Re-run unit, extended, formatting, lint, and
relevant E2E checks, then obtain maintainer approval.

Do not post this review upstream without human verification.
