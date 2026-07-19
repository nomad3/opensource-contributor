# Prometheus Operator PR #8695 review

- Pull request: <https://github.com/prometheus-operator/prometheus-operator/pull/8695>
- Issue: <https://github.com/prometheus-operator/prometheus-operator/issues/8692>
- Reviewed commit: `f127a0fc3788e508ae4baa2eff79018416b043ca`
- Review date: 2026-07-19
- Upstream communication: not posted
- Initial verdict: **NO-GO**
- Suggestion-patch verdict: **GO**

## Scope

The pull request mirrors Alertmanager's top-level `event_recorder` configuration
inside the operator so file, webhook, and Kafka outputs can survive the
operator's strict unmarshal and secret-preserving marshal path.

The review compared the patch field-by-field with Alertmanager v0.33.1,
inspected the operator's parse and sanitize pipeline, ran focused tests, and
used Claude Fable 5 as an independent adversarial reviewer.

## Blocking

### Add an Alertmanager 0.33.0 version gate

`pkg/alertmanager/amcfg.go` sanitizes raw configuration against the version of
Alertmanager managed by the custom resource. It removes fields that the target
version cannot parse, including `mute_time_intervals` before 0.22.0 and
`time_intervals` before 0.24.0.

PR #8695 adds `alertmanagerConfig.EventRecorder`, but `sanitize()` never removes
it for older Alertmanager versions. Alertmanager's changelog shows that
`event_recorder` was introduced in 0.33.0. The operator validates raw input with
its vendored Alertmanager v0.33.1 parser, so that validation succeeds even when
the deployed Alertmanager is 0.32.x.

Failure sequence:

1. A user manages Alertmanager `< 0.33.0`.
2. Their raw configuration secret contains `event_recorder`.
3. The operator's vendored v0.33.1 parser accepts it.
4. The operator preserves and emits the unsupported field.
5. The running Alertmanager rejects the generated configuration on reload.

Before this patch the operator rejects the unknown field early. After the
patch, without a version gate, the incompatibility moves into the running
Alertmanager and can prevent unrelated alert-routing updates from applying.

The fix should follow the existing sanitizer convention: when
`amVersion.LT(semver.MustParse("0.33.0"))`, log a warning and set
`c.EventRecorder = nil`. Add a focused sanitizer test covering versions below
and at the boundary.

## Important

### Exercise every mirrored field

The golden input covers all three output types but omits these newly mirrored
fields:

- Kafka: `client_id`, `format`, `buffer_size`, and `tls_config`
- Webhook HTTP configuration: every subfield except `basic_auth`

There is no reflection-based drift test for the local mirrors. Extending the
golden case to exercise all newly introduced fields would ensure future field
removal or a wrong YAML tag fails `TestLoadConfig`.

## Optional follow-up

The pre-existing local `tlsConfig` mirror lacks newer inline TLS material and
reference fields from `prometheus/common` v0.70.0. A valid raw configuration
using those fields fails loudly during the operator's strict unmarshal. This is
not introduced by PR #8695 and is shared by existing HTTP client consumers, so
it belongs in a separate issue.

## Checks that passed

- File, webhook, and Kafka output fields and YAML tags match Alertmanager
  v0.33.1.
- Required fields retain non-`omitempty` tags.
- Secret-bearing values use the repository's established local mirror pattern.
- Upstream strict validation still runs before the local strict unmarshal.
- Pointer durations preserve explicit zero values without introducing defaults.
- The feature flag is not required for parsing on Alertmanager 0.33 or newer.
- The commit includes a DCO sign-off.
- All required upstream CI checks pass.

Local validation:

```text
go test ./pkg/alertmanager -run 'TestLoadConfig|TestEventRecorderConfig' -count=1
ok github.com/prometheus-operator/prometheus-operator/pkg/alertmanager

git diff origin/main...HEAD --check
clean
```

## Draft upstream review

> Thanks for adding the secret-preserving mirror and round-trip coverage. I
> found one version-compatibility issue: `event_recorder` was introduced in
> Alertmanager 0.33.0, but `alertmanagerConfig.sanitize()` does not remove the
> field when the managed Alertmanager version is older. Because the operator
> validates with its vendored v0.33.1 parser, a raw secret containing
> `event_recorder` is accepted even for a 0.32.x deployment, then emitted to an
> Alertmanager that cannot parse it. Could you add the same kind of version gate
> used for `mute_time_intervals` and `time_intervals`—warn and set
> `c.EventRecorder = nil` below 0.33.0—plus a boundary sanitizer test?
>
> It would also strengthen the mirror contract if the golden case exercised the
> remaining Kafka fields (`client_id`, `format`, `buffer_size`, `tls_config`)
> and more than one `http_config` credential path, since the current tests are
> the only field-drift guard.

## Validated suggestion patch

The version blocker now has a minimal, signed-off patch:

- commit: `351e53a4`
- artifact:
  `.contrib/patches/prometheus-operator-8695-version-gate.patch`
- handoff:
  `.contrib/handoffs/prometheus-operator-8695-version-gate.md`

Both the focused sanitizer/load tests and the complete
`./pkg/alertmanager` package pass. Claude Fable 5 independently cross-reviewed
the suggestion and returned GO with no blocking or important findings after
confirming the 0.33.0 boundary, sanitizer convention, and preservation/removal
goldens.
