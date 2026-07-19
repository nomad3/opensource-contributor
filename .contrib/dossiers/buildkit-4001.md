# Issue dossier

## Identity

- Repository: moby/buildkit
- Issue: [#4001 — Tracing documention only covers Jaeger](https://github.com/moby/buildkit/issues/4001) (open, labels: `help wanted`, `kind/docs`)
- Upstream commit inspected: `6dd06999d5d369a217c3f3259a420f507e2db2c7` (master, 2026-07-17)
- Checked at: 2026-07-18

## 1. Expected behavior

The README "OpenTelemetry support" section (README.md:808-824) documents only Jaeger via
`JAEGER_TRACE`. Expected: documentation of the OTLP exporter, which the code fully
supports and which maintainer review on PR #6813 confirmed should become the primary
documented path.

Verified implementation behavior (`util/tracing/detect/`):

- OTLP trace export activates when `OTEL_TRACES_EXPORTER=otlp`, or
  `OTEL_EXPORTER_OTLP_ENDPOINT` / `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` is set
  (otlp.go:27).
- Protocol from `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`, else
  `OTEL_EXPORTER_OTLP_PROTOCOL`, else default `grpc`. Supported: `grpc`,
  `http/protobuf`; `http/json` explicitly unsupported; other values error
  (otlp.go:32-50). OTLP metrics export exists with parallel env vars (otlp.go:55-82).
- Exporter registry: `otlp` priority 10, legacy `jaeger` priority 11, `none` 1000;
  lowest priority wins auto-detection; `OTEL_TRACES_EXPORTER` selects explicitly
  (detect.go:47-92, detect.go:153-158).
- Jaeger remains as a compatibility shim using the deprecated
  `go.opentelemetry.io/otel/exporters/jaeger` (`JAEGER_TRACE`, `OTEL_EXPORTER_JAEGER_*`;
  jaeger/jaeger.go:11-21).
- Both binaries detect from env: `cmd/buildkitd/main.go:63,862` and
  `cmd/buildctl/main.go:23`; buildctl additionally always delegates client spans to the
  daemon (`cmd/buildctl/common/trace.go:28`, `util/tracing/delegated`).

## 2. Reproduction procedure

Documentation gap reproduces by reading README.md:808-824 — no OTLP mention.

The detector behavior was validated from source and with:

```bash
go test ./util/tracing/detect/...
```

Result on macOS arm64 at `6dd0699`: PASS for `util/tracing/detect`; the Jaeger
compatibility subpackage has no tests.

An end-to-end Collector example was not run because unresolved contribution ownership
blocks implementation. A future reproduction must provide a concrete Collector
configuration and account for Docker Desktop networking rather than publish placeholder
commands.

## 3. User and operational impact

Operators wiring BuildKit into standard OTLP pipelines (Collector, Tempo, Datadog,
vendor backends) find no documentation; Jaeger-only docs push users toward a deprecated
exporter path. Docs-only issue; no runtime defect.

## 4. Relevant production files

- README.md:808-824 (section to rewrite) — only file the patch should touch
- util/tracing/detect/{detect.go,otlp.go,jaeger/jaeger.go} (behavior source of truth; not to be modified)

## 5. Existing tests and missing coverage

No runtime regression test is appropriate for a README-only change. The relevant
repository CI gate is doctoc TOC validation (`make validate-doctoc`, Makefile:85-87;
failed for real on PR #6813 per maintainer comment).

## 6. Smallest acceptable patch

Defined by maintainer review (tonistiigi, PR #6813, 2026-06-03): rewrite the whole
"OpenTelemetry support" section so it is not Jaeger-specific — no `JAEGER_TRACE`
mention, keep a Jaeger all-in-one example using OTEL env vars only, do not enumerate
grpc/http options (defer to OTEL docs), optionally one tested backend example. Single
README.md hunk. Run `make doctoc` if the section heading changes or validation reports a
TOC diff.

## 7. Compatibility and rollback risks

None at runtime (docs-only). Documentation risk: dropping `JAEGER_TRACE` from docs while
code still honors it — explicitly sanctioned by maintainer review. Trivial rollback.

## 8. Security, observability, and performance implications

None beyond documenting an existing telemetry path. The public security-reporting
instructions in `.github/SECURITY.md` and `.github/CONTRIBUTING.md` direct reports to a
private channel and are not implicated. Observed unrelated latent defect while reading:
detect.go:48 parses the literal string `"OTEL_IGNORE_ERROR"` instead of the env value,
so `OTEL_IGNORE_ERROR` can never activate — out of scope here; candidate separate
upstream report.

## 9. Exact validation commands

```bash
go test ./util/tracing/detect/...
make validate-doctoc
```

`make doctoc` regenerates the TOC if required. `make validate-doctoc` requires Docker
with Buildx Bake. DCO sign-off with the contributor's real name is required on every
commit (`.github/CONTRIBUTING.md`, "Sign your work").

## 10. Ownership and overlap evidence

- Assignee: none
- Linked PRs: [#6813](https://github.com/moby/buildkit/pull/6813) "docs: add OTLP
  exporter documentation" by dpk-jr (created 2026-05-31, README.md +31, `Closes #4001`;
  announced in an issue comment). State CLOSED, not merged.
  - tonistiigi (maintainer): scope review 2026-06-03; "Missing DCO"; "doctoc error also
    real in CI"; CHANGES_REQUESTED 2026-06-12 against `904bc73`; closed 2026-07-06 with
    "Reopen if you have updates".
  - Author's fork branch `dpk-jr/buildkit:docs/add-otlp-otlp-documentation` still exists
    at `904bc73` (no updates since 2026-05-31), verified 2026-07-18 via GitHub API.
- Recent related PR search found no merged change addressing this README section. The
  search did find tracing implementation work: merged PRs #6874 and #6958, closed
  unmerged PR #6918, and open PR #6588. None supersedes the requested documentation;
  #6958 is relevant context for preserving build-provided OTEL variables.
- Maintainer discussion: the #6813 review above is the authoritative scope statement.

## 11. Questions requiring maintainer input

- None on technical scope (review on #6813 settles it). The open question is
  procedural: whether dpk-jr will reopen. "Reopen if you have updates" was addressed to
  the prior author only 12 days ago; superseding now would contest ownership.
- Unverified: current state of the docs.docker.com OpenTelemetry page (docker/docs
  repo) — secondary target named in the issue.

## Decision

- Status: blocked
- Next exact action: wait; re-check PR #6813 (reopened? branch updated?) and issue
  assignee state around 2026-08-01. If the prior author remains inactive, ask in issue
  #4001 whether picking it up is welcome (human posts) before any patch.
- Resumable stopping point: full evidence captured at upstream `6dd0699`; clone under
  `upstreams/buildkit`; focused detector tests pass; no BuildKit files modified; nothing
  committed or posted.
