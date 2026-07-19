# Bilby #1114 tidal round-trip reproducer

This zero-dependency reproducer isolates the arithmetic failure reported in
[bilby-dev/bilby #1114](https://github.com/bilby-dev/bilby/issues/1114).
It mirrors the forward and inverse tidal-deformability formulas from Bilby commit
[`28fca227`](https://github.com/bilby-dev/bilby/commit/28fca22709f75bce1417aaf4438f3195993c550b).

The evidence boundary is deliberately narrow:

- it proves that a valid `lambda_1 = 0.0` can round-trip through
  `lambda_tilde` and `delta_lambda_tilde` to a negative float;
- it does not import Bilby, install LALSuite, generate a waveform, or reproduce the
  issue-reported downstream LALSimulation error;
- it does not decide which representation should win when a caller supplies
  inconsistent component and derived values.

## Run

```bash
python3 reproducers/bilby-1114/reproduce.py
python3 -m unittest discover \
  -s reproducers/bilby-1114 \
  -p 'test_*.py' \
  -v
```

Expected key result:

```text
"roundtrip_lambda_1": -2.45587692656649e-14
```

That negative value is sufficient to establish the conversion mechanism. The issue
reports that LALSimulation later rejects it because tidal deformabilities must be
non-negative.

## Design evidence

Bilby's original derived-tidal implementation added support for sampling in
`lambda_tilde` and the secondary parameter then named `delta_lambda` (now
`delta_lambda_tilde`), reconstructed component lambdas for the waveform, and then
generated the complementary tidal representation in the output. Mixed dictionaries
are therefore a normal post-processing state.

Current tests separately cover:

- `lambda_tilde` plus `delta_lambda_tilde`;
- `lambda_tilde` alone;
- `lambda_1` alone.

They do not pass the complete mixed output through the converter a second time. See
the [dossier](../../.contrib/dossiers/bilby-1114.md) and
[handoff](../../.contrib/handoffs/bilby-1114.md) for the remaining contract and
dispatch gates.
