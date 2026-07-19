# OpenTelemetry Python Contrib #4816 dossier

## Decision

**WAITING — obtain maintainer direction before implementation.**

The issue is open, unassigned, and has no comments or overlapping open pull
request, but the smallest correct implementation depends on two decisions that
are not encoded in either repository:

1. whether the new GenAI OpenAI instrumentation replaces or coexists with the
   existing `opentelemetry-instrumentation-openai-v2` bootstrap mapping; and
2. how contrib's generator should ingest and maintain metadata for packages
   released from the external GenAI repository.

The repository's `AGENTS.md` requires implementation direction to be agreed
with maintainers first and forbids agents from posting issue or pull-request
comments. No upstream communication or code change was made.

## Upstream state

- Project: `open-telemetry/opentelemetry-python-contrib`
- Issue: [#4816 — Update bootstrap_gen to detect GenAI libraries with instrumentations](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4816)
- Checked: 2026-07-19
- Evidence refreshed: 2026-07-19T03:10:02Z
- State: open
- Assignees: none
- Comments: none
- Overlapping open PR search (`4816 OR bootstrap GenAI`): none
- Contrib revision inspected: `a8359fd8ac2ec5d3e22561a38bd57eee168540da`
- GenAI revision inspected: `dc2ee00a1173ee7db9800489b9dff7e8a4db1518`

## Expected behavior

When a supported GenAI framework is installed,
`opentelemetry-bootstrap --action=install` should identify and install the
corresponding released instrumentation from
`open-telemetry/opentelemetry-python-genai`.

The issue names five framework instrumentations:

| Framework requirement | Released instrumentation |
| --- | --- |
| `google-genai >= 1.32.0, < 3` | `opentelemetry-instrumentation-google-genai` |
| `openai-agents >= 0.3.3` | `opentelemetry-instrumentation-genai-openai-agents` |
| `openai >= 1.26.0` | `opentelemetry-instrumentation-genai-openai` |
| `langchain >= 0.3.21` | `opentelemetry-instrumentation-genai-langchain` |
| `anthropic >= 0.51.0` | `opentelemetry-instrumentation-genai-anthropic` |

`opentelemetry-util-genai` has no framework requirement of its own and is a
dependency of instrumentations, so it should not independently appear in the
bootstrap detection list.

## Current behavior and evidence

Loading the generated list on current contrib `main` produced:

```text
openai [('openai >= 1.26.0', 'opentelemetry-instrumentation-openai-v2')]
google-genai []
langchain []
anthropic []
openai-agents []
```

The issue says bootstrap currently installs old contrib `google-genai` and
`langchain` packages. Current source instead excludes those packages from
generation, and the generated list contains neither mapping. This difference
should be clarified, but does not prevent adding the missing mappings.

The important conflict is OpenAI: `_find_installed_libraries()` yields every
matching entry. Adding `opentelemetry-instrumentation-genai-openai` without
removing or otherwise resolving the existing `openai-v2` entry would ask pip to
install both instrumentations for the same installed framework.

## Generation boundary

`scripts/generate_instrumentation_bootstrap.py` scans packaging metadata under
the contrib repository's local `instrumentation/` and
`instrumentation-genai/` trees. The new packages and their `instruments`
metadata live in the separate `opentelemetry-python-genai` repository.

The contrib repository clearly owns its generator and generated
`bootstrap_gen.py`. There is currently no mechanism for that generator to
consume external repository metadata. What remains undecided is the
metadata-source design and its maintenance contract:

- maintain a small external mapping table in the contrib generator;
- generate and publish a manifest from the GenAI repository; or
- define a cross-repository metadata contract consumed during generation.

Choosing among these is a maintainer decision about metadata provenance and
cross-repository maintenance, not a mechanical implementation detail.

## User and operational impact

Without this change, distro users must know and install the new GenAI
instrumentations manually. A wrong implementation is worse than omission:
installing two OpenAI instrumentations may produce duplicate hooks or spans,
while stale cross-repository metadata may silently install an obsolete or
incompatible package.

## Relevant files

Contrib:

- `scripts/generate_instrumentation_bootstrap.py`
- `scripts/otel_packaging.py`
- `opentelemetry-instrumentation/src/opentelemetry/instrumentation/bootstrap.py`
- `opentelemetry-instrumentation/src/opentelemetry/instrumentation/bootstrap_gen.py`
- `opentelemetry-instrumentation/tests/test_bootstrap.py`

GenAI:

- each released instrumentation's `pyproject.toml`, which defines its
  `instruments` requirement

## Smallest acceptable patch after agreement

1. Add the agreed external mapping source to the existing generator.
2. Resolve the existing `openai-v2` mapping according to maintainer direction.
3. Regenerate `bootstrap_gen.py`; do not hand-edit only the generated file.
4. Add deterministic tests for all five framework-to-instrumentation mappings.
5. Exercise `_find_installed_libraries()` and assert that each installed
   framework selects exactly one intended instrumentation, including OpenAI.
6. Add the coordinated-package changelog fragment at
   `.changelog/<PR>.added`.

No dependency updates, framework instrumentation changes, or unrelated
generator refactors belong in this patch.

## Validation contract

After scope agreement:

```bash
uv run tox -e generate
git diff -- opentelemetry-instrumentation/src/opentelemetry/instrumentation/bootstrap_gen.py
before="$(shasum -a 256 opentelemetry-instrumentation/src/opentelemetry/instrumentation/bootstrap_gen.py)"
uv run tox -e generate
test "$before" = "$(shasum -a 256 opentelemetry-instrumentation/src/opentelemetry/instrumentation/bootstrap_gen.py)"
uv run tox -e py312-test-opentelemetry-instrumentation-wrapt2
uv run tox -e lint-opentelemetry-instrumentation
uv run pre-commit run ruff --all-files
```

The first diff is reviewed as the intentional generated change. The second
generation and hash comparison prove the output is deterministic without
assuming it matches `HEAD`. The focused bootstrap tests should run before
broader suites. The Python version used for lint should continue to follow the
repository's current tox and CI convention if it changes before implementation.

## Compatibility, security, and performance risks

- **Compatibility:** selecting both OpenAI instrumentations may double
  instrument calls or make initialization order-dependent.
- **Release compatibility:** external packages use independent `1.0b*`
  versions; contrib's normal development-version pinning must not be applied.
- **Drift:** a duplicated static table can diverge from GenAI package metadata.
- **Supply chain:** bootstrap installs package names automatically, so mappings
  must be explicit, reviewed, and covered by tests.
- **Performance:** detection is a short static scan; the mapping count itself is
  not material. Duplicate runtime instrumentation is the meaningful risk.
- **Observability:** incorrect coexistence can create duplicate telemetry,
  misleading users and increasing ingestion volume.

## Maintainer decisions the user should raise in their own words

1. Should `opentelemetry-instrumentation-genai-openai` replace
   `opentelemetry-instrumentation-openai-v2` in bootstrap, or is coexistence
   intentionally supported?
2. Should the contrib generator maintain a reviewed external mapping table, or
   consume a source-of-truth manifest published by the GenAI repository?
3. Should bootstrap include only already released GenAI packages, with future
   releases added explicitly?
4. Are the framework version bounds from the GenAI packages the intended
   bootstrap detection bounds?

## Stop condition

Do not implement merely because the issue is unassigned. Resume only after a
human contributor obtains maintainer direction for the OpenAI transition and
the external metadata ingestion and maintenance contract.
