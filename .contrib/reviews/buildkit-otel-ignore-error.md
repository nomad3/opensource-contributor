# BuildKit OTEL_IGNORE_ERROR cross-review

## Scope

Reviewed only:

- `util/tracing/detect/detect.go`
- `util/tracing/detect/detect_test.go`

## Independent findings

- The test was independently run against unmodified `master` using a Go overlay and
  failed for the expected unsupported-exporter error.
- Both trace and metric exporter paths instantiate the shared generic function.
- The default-error subtest prevents accidental unconditional suppression.
- The invalid exporter exits before detector invocation, so the test does not dial a
  backend or depend on global detector registration.
- `t.Setenv` safely restores process environment and the test is not parallel.
- The one-line change exactly restores the expression removed by the 2024 refactor.

## Validation

- Focused regression test: PASS after fix
- Full detector package tests: PASS
- Go vet: PASS
- Go formatting: clean

## Verdict

GO. No blocking or important findings. The diff is minimal, DRY, convention-aligned,
and ready for human-approved publication.
