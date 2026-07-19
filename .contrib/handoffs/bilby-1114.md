# Bilby #1114 reconnaissance handoff

## Objective

Determine the intended semantics when Bilby's binary-neutron-star conversion
receives both component tidal deformabilities (`lambda_1`, `lambda_2`) and derived
tidal parameters (`lambda_tilde`, `delta_lambda_tilde`), then prepare the smallest
regression fix only if maintainers confirm that contract.

## Completed

- Revalidated [bilby-dev/bilby #1114](https://github.com/bilby-dev/bilby/issues/1114)
  at `2026-07-19T03:37:37Z`: open, unassigned, and with no linked branch or pull
  request.
- Inspected upstream commit
  `28fca22709f75bce1417aaf4438f3195993c550b`.
- Located the overwrite in
  `bilby/gw/conversion.py::convert_to_lal_binary_neutron_star_parameters`.
- Inspected `test/gw/conversion_test.py`; mixed component-plus-derived input and
  repeated-conversion idempotency are not covered.
- Reproduced the numerical round trip using the current conversion formulas and
  NumPy, without LALSuite or a full Bilby environment.
- Added a zero-dependency reproducer and three regression-oracle tests at
  `reproducers/bilby-1114`.
- Traced the design to historical merge commit `bca29246`: derived tidal sampling
  and generation of both representations were introduced together, so mixed output
  is expected.
- Removed the disposable checkout after recording the source SHA and evidence.

## Evidence

- Input:

  ```text
  mass_1 = 7.320188129088971
  mass_2 = 1.4957247709090036
  lambda_1 = 0.0
  lambda_2 = 1097.4026147742702
  ```

- Derived and reconstructed values:

  ```text
  lambda_tilde = 11.340939966673643
  delta_lambda_tilde = 5.98106544849901
  reconstructed lambda_1 = -2.45587692656649e-14
  reconstructed lambda_2 = 1097.402614774269
  ```

- Result: the second conversion overwrites an explicit, valid zero with a negative
  roundoff value. The issue report shows LALSimulation rejecting that value during
  post-processing after sampling completed.
- Full package import result: stopped at the absent declared dependency
  `array_api_compat`; dependencies were not installed because the arithmetic
  reproducer already isolated the conversion defect.
- Detailed artifact:
  [`.contrib/dossiers/bilby-1114.md`](../dossiers/bilby-1114.md).
- Reproducer:
  [`reproducers/bilby-1114`](../../reproducers/bilby-1114).

## Current diff

No Bilby upstream source or test files were changed. The Bilby-specific tracker diff
contains the candidate dossier, this handoff, and the standalone files under
`reproducers/bilby-1114`.

## Next exact action

The next allowed action is read-only: on the next Observer cycle, recheck the issue,
assignee, comments, linked development work, and open pull requests for a maintainer
decision on:

> When `generate_all_bns_parameters` produces a complete mixed representation and
> that output is converted again, should complete component lambdas be preserved?
> For independently supplied inconsistent or partial mixed inputs, should Bilby
> reject them or retain the current derived-value precedence?

If no public guidance appears, ask that question only after the user explicitly
authorizes upstream contact. Implementation may begin only when maintainers define
the contract and the Observer Manager grants a free slot at dispatch time. Then:

1. Create a disposable checkout at current `main` and install only the
   project-declared test dependencies in an isolated environment.
2. Add an idempotency regression for the complete output of
   `generate_all_bns_parameters`, plus only the partial/inconsistent cases required
   by the confirmed contract.
3. Preserve the existing derived-only conversion tests.
4. Make the smallest production change that implements the confirmed semantics.
5. Run the focused conversion tests, the repository's required formatting/linting,
   and the relevant gravitational-wave test slice before considering publication.

## Risks or unanswered questions

- The issue author's expected behavior is a proposal, not yet maintainer-confirmed
  policy.
- Callers may currently pass inconsistent component and derived representations;
  silently changing which representation wins could alter their results.
- A numerical clamp would hide the precedence problem and would not define behavior
  for other inconsistent values.
- LALSuite is not needed for the regression but may be useful for an optional
  downstream integration check.
- The Observer Manager recorded 96% volume use and 20 GiB available at
  `2026-07-19T02:00:00Z`; recheck this time-sensitive state before creating any
  future checkout, and keep that checkout disposable.

## Do not do

- Do not begin Bilby implementation unless the Observer Manager reports a free slot
  at dispatch time. BuildKit PR #6966 is the current occupant.
- Do not contact maintainers, claim the issue, push a branch, or open a pull request
  without explicit user authorization.
- Do not infer maintainer agreement from the reporter's suggested patch.
- Do not install LALSuite or download large gravitational-wave datasets merely to
  reproduce a defect already isolated with a CPU-only arithmetic test.
- Do not clamp small negative lambdas or refactor unrelated conversion code.
