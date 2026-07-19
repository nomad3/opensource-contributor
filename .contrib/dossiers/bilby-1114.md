# Bilby #1114 — BNS tidal-parameter conversion precedence

## Identity

- Repository: `bilby-dev/bilby`
- Issue: [#1114](https://github.com/bilby-dev/bilby/issues/1114)
- Upstream commit inspected: `28fca22709f75bce1417aaf4438f3195993c550b`
- Checked at: `2026-07-19T03:37:37Z`
- Ownership: open, unassigned, no linked or matching open pull request found

## Scientific and operational impact

Bilby's binary-neutron-star post-processing can receive both component tidal
deformabilities (`lambda_1`, `lambda_2`) and their derived representation
(`lambda_tilde`, `delta_lambda_tilde`). The current conversion reconstructs and
overwrites the component values whenever derived values exist.

For the reported neutron-star–black-hole injection, a valid explicit
`lambda_1=0.0` becomes a small negative value. LALSimulation rejects negative
tidal deformability, so an inference that ran for more than a day can fail during
post-processing even though sampling completed.

## Source finding

`bilby/gw/conversion.py::convert_to_lal_binary_neutron_star_parameters` checks
`delta_lambda_tilde` and `lambda_tilde` and reconstructs component lambdas without
first testing whether component values are already present:

```python
if "delta_lambda_tilde" in converted_parameters:
    converted_parameters["lambda_1"], converted_parameters["lambda_2"] = ...
elif "lambda_tilde" in converted_parameters:
    converted_parameters["lambda_1"], converted_parameters["lambda_2"] = ...
```

This establishes the mechanical root cause. It does not establish whether that
precedence is the intended public contract.

## Reproduction

The numerical failure can be reproduced from the formulas at inspected commit
`28fca22709f75bce1417aaf4438f3195993c550b` without Bilby runtime dependencies
or LALSuite:

```text
mass_1: 7.320188129088971
mass_2: 1.4957247709090036
input lambda_1: 0.0
input lambda_2: 1097.4026147742702
lambda_tilde: 11.340939966673643
delta_lambda_tilde: 5.98106544849901
round-trip lambda_1: -2.45587692656649e-14
round-trip lambda_2: 1097.402614774269
```

Importing the full checkout was not required for this arithmetic reproduction.
A full package import in the bare environment stopped at the missing declared
dependency `array_api_compat`; no dependency installation was attempted.

LALSuite is necessary only to reproduce the downstream waveform rejection, not
the conversion defect.

A durable zero-dependency reproducer and test oracle now lives at
[`reproducers/bilby-1114`](../../reproducers/bilby-1114). It records the exact
source commit and keeps the locally reproduced arithmetic separate from the
issue-reported LALSimulation failure.

## Historical design evidence

The original derived-tidal implementation was merged in
[`bca2924`](https://github.com/bilby-dev/bilby/commit/bca29246e40286e0eeb57fc403982b2d37d1303e).
It introduced all of these behaviors together:

- sample in `lambda_tilde` and the secondary parameter then named `delta_lambda`
  (now `delta_lambda_tilde`);
- reconstruct `lambda_1` and `lambda_2` for the waveform;
- run `generate_tidal_parameters` after base conversion so the returned sample
  contains both representations.

Complete mixed dictionaries are therefore an expected post-processing product, not
merely malformed caller input. The history does not define which representation
should win when independently supplied values are inconsistent.

## Existing test gap

`test/gw/conversion_test.py` covers:

- conversion from `lambda_tilde` plus `delta_lambda_tilde`;
- conversion from `lambda_tilde`;
- conversion from `lambda_1`;
- forward and inverse tidal formulas.

It does not cover:

- a dictionary containing both component and derived tidal representations;
- preservation of explicitly supplied zero values;
- idempotency when generated parameters are converted again.

The existing `test_lambda_1` case also establishes the current component-only partial
behavior: when only `lambda_1` is supplied, Bilby derives `lambda_2` from the
mass-scaled relation. It does not establish semantics for a partial component
representation mixed with complete derived values.

## Smallest future regression shape

After maintainers define mixed-representation behavior, add focused cases that:

1. start with `mass_1`, `mass_2`, `lambda_1=0.0`, and `lambda_2`;
2. derive `lambda_tilde` and `delta_lambda_tilde`;
3. pass the mixed dictionary to
   `convert_to_lal_binary_neutron_star_parameters`;
4. exercise complete, partial, and inconsistent mixed representations;
5. assert the maintainer-selected preservation, reconstruction, or rejection
   behavior;
6. verify that derived-only inputs continue to reconstruct components.

Do not prescribe a guard before partial mixed input is defined: reconstructing both
components when only one is missing could still overwrite an explicit value. No
tolerance clamp or unrelated waveform change is justified.

## Unresolved contract

The issue author states that explicit component lambdas should take precedence and
supplies a proposed guard, but the inspected tests and history do not contain
maintainer-authored precedence guidance. No maintainer response was visible when
revalidated. Changing the order can affect callers that currently supply inconsistent
component and derived values and expect derived values to win.

Maintainer confirmation is required before implementation:

> When both complete component lambdas and complete derived tidal parameters are
> present, should Bilby preserve the component representation, reject inconsistent
> inputs, or continue prioritizing the derived representation?

## Decision

- Status: reconnaissance
- Importance: high scientific correctness; bounded technical fix
- Ready for implementation: no
- Evidence completed: source mapping, historical mixed-output design evidence,
  deterministic arithmetic reproducer, and existing-test gap
- Exact next action: monitor for maintainer guidance; if none appears, ask whether
  complete component values should be preserved on re-conversion, only after the
  user authorizes upstream contact
- Handoff: [`.contrib/handoffs/bilby-1114.md`](../handoffs/bilby-1114.md)
- Stop condition: do not implement unless the Observer Manager reports an available
  slot at dispatch time and the contract is maintainer-confirmed. BuildKit PR #6966
  is the current slot occupant, not the durable gate.
