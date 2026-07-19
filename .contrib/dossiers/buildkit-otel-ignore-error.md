# Issue dossier

## Identity

- Repository: moby/buildkit
- Upstream issue: none found
- Draft pull request: [#6966](https://github.com/moby/buildkit/pull/6966)
- Upstream commit inspected: `6dd06999d5d369a217c3f3259a420f507e2db2c7` (`master`)
- Local patch commit: `14e0dfbd`
- Checked at: 2026-07-18

## Expected behavior

When `OTEL_IGNORE_ERROR` is a valid true value, BuildKit should suppress exporter
detection errors. This was the behavior before tracing refactor commit `228e250d`.

## Root cause

The refactor replaced:

```go
strconv.ParseBool(os.Getenv("OTEL_IGNORE_ERROR"))
```

with:

```go
strconv.ParseBool("OTEL_IGNORE_ERROR")
```

Parsing the literal variable name always fails, leaving `ignoreErrors` false. The same
refactor added three branches that consume `ignoreErrors`, so retaining the feature was
clearly intended.

## Impact

Since the refactor, `OTEL_IGNORE_ERROR=true` cannot suppress errors from:

- an unknown explicitly selected trace or metric exporter;
- an explicitly selected exporter that fails detection;
- an auto-detected exporter that fails detection.

The fix restores previously intended behavior. Operators already carrying this setting
will again receive silent exporter-error suppression, which should be called out in the
pull-request description.

## Ownership and overlap

`gh` issue, PR, and commit searches found no existing work mentioning
`OTEL_IGNORE_ERROR` or the equivalent failure behavior. The introducing commit is
`228e250d` from March 2024.

## Minimal patch

- Restore `os.Getenv("OTEL_IGNORE_ERROR")` in `detectExporter`.
- Add one table-driven test covering error-by-default and ignore-error behavior for
  both trace and metric exporter paths.
- No dependency, API, documentation, or unrelated formatting changes.

## Test evidence

Before the production fix, the regression test failed with:

```text
unsupported opentelemetry exporter invalid
```

After the fix:

```bash
go test ./util/tracing/detect/... -run TestDetectExporterIgnoreErrors -v
go test ./util/tracing/detect/...
go vet ./util/tracing/detect/...
gofmt -l util/tracing/detect/
```

All tests and vet passed; `gofmt -l` returned no files.

## Risks

- The test deliberately uses an unknown exporter name, avoiding network calls and
  mutation of the package-global detector registry.
- `t.Setenv` restores environment state and prevents unsafe parallel execution.
- The auto-detection-loop error branch is not tested because doing so would require
  mutating global detector state; both public trace and metric generic instantiations
  are covered without that risk.

## Decision

- Status: draft pull request open
- Next action: monitor CI and respond narrowly to maintainer review.
- Publication: `nomad3/buildkit:fix/otel-ignore-error` at `14e0dfbd`
- Initial checks: DCO passed; repository workflows pending.
