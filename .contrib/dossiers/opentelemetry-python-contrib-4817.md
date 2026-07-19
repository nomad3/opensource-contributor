# OpenTelemetry Python Contrib #4817 dossier

## Decision

**WAITING — technically scoped, but not authorized for implementation.**

The issue is open, unassigned, has no comments, and has no identified
overlapping pull request. The failure has a narrow, evidence-backed cause in
the SQLAlchemy instrumentation's weak-reference cleanup. The repository's
`AGENTS.md` requires a human to agree implementation direction with
maintainers before an AI-assisted implementation begins. BuildKit PR #6966
also remains the control plane's single published implementation.

No upstream communication or source change was made.

## Upstream state

- Project: `open-telemetry/opentelemetry-python-contrib`
- Issue: [#4817 — Flaky sqlalchemy tests on Pypy](https://github.com/open-telemetry/opentelemetry-python-contrib/issues/4817)
- Evidence refreshed: 2026-07-19T03:20:34Z
- State: open
- Assignees: none
- Comments: none
- Linked closing PRs: none
- Open/closed PR searches for `4817`, `flaky sqlalchemy pypy`,
  `weak_ref_target sqlalchemy`, and `remove event listener garbage collected`:
  no overlapping fix found
- Revision inspected: `a8359fd8ac2ec5d3e22561a38bd57eee168540da`

## Reported failure

The first failing test reaches
`SQLAlchemyInstrumentor().uninstrument()` during teardown. SQLAlchemy receives
`target=None` while removing the `checkout` event listener and raises:

```text
sqlalchemy.exc.InvalidRequestError:
No such event 'checkout' for target 'None'
```

The next test warns:

```text
Attempting to instrument while already instrumented
```

and then fails because the expected SQL-commented query was not emitted.

## Root cause

`EngineTracer._register_event_listener()` intentionally stores a weak reference
to each SQLAlchemy engine so instrumentation does not keep disposed engines
alive. `remove_all_event_listeners()` currently resolves that weak reference
twice:

```python
if weak_ref_target() is not None:
    remove(weak_ref_target(), identifier, func)
```

The guard does not keep the engine alive. A garbage collector may reclaim it
between the two calls, particularly under PyPy's collection behavior. The
first call can therefore return an engine while the second returns `None`.
That is exactly consistent with the reported traceback: execution passed the
guard but SQLAlchemy's `remove()` received `None`.

The teardown exception prevents `BaseInstrumentor.uninstrument()` from
finishing its state reset. The subsequent “already instrumented” warning and
SQL-commenter assertion are therefore a cascade from the first failure, not
evidence of a second independent defect.

## Historical intent

Merged PR
[#1771](https://github.com/open-telemetry/opentelemetry-python-contrib/pull/1771)
introduced weak references specifically to avoid retaining disposed engines.
Its stated cleanup contract is to remove listeners only for targets that have
not been garbage-collected. Holding one local strong reference for the
duration of `remove()` preserves that contract and does not restore the
original memory leak.

## Smallest acceptable patch

Resolve each weak reference once and keep the result in a local variable:

```python
target = weak_ref_target()
if target is not None:
    remove(target, identifier, func)
```

Do not change listener registration, finalizer behavior, instrumentation state,
or SQL-commenter assertions in the same patch.

## Regression test contract

Add a deterministic unit test around
`EngineTracer.remove_all_event_listeners()`:

1. provide a callable weak-reference substitute whose first invocation returns
   a target and whose second invocation returns `None`;
2. patch SQLAlchemy's imported `remove()` function;
3. invoke `remove_all_event_listeners()`;
4. assert the weak-reference callable was invoked exactly once;
5. assert `remove()` received the retained target, identifier, and callback;
6. assert `_remove_event_listener_params` is cleared; and
7. restore the class-level list in a patch context or `try/finally` so a failed
   assertion cannot poison later tests.

This test fails on current `main` without relying on nondeterministic garbage
collection: current code calls the substitute twice and passes `None` to
`remove()`. It passes only when the target is resolved once.

An additional PyPy stress loop is optional evidence, not a substitute for the
deterministic regression test.

## Relevant files

- `instrumentation/opentelemetry-instrumentation-sqlalchemy/src/opentelemetry/instrumentation/sqlalchemy/engine.py`
- `instrumentation/opentelemetry-instrumentation-sqlalchemy/tests/test_sqlalchemy.py`
- `.changelog/<PR>.fixed`

## Validation contract

Use the current tox factors from `tox.ini`:

```bash
uv run tox -e py312-test-instrumentation-sqlalchemy-1
uv run tox -e pypy3-test-instrumentation-sqlalchemy-1
uv run tox -e lint-instrumentation-sqlalchemy
uv run pre-commit run ruff --all-files
```

The CPython environment proves the deterministic regression. PyPy is not
currently installed on this workstation and no prepared PyPy tox environment
exists in the disposable clone. An implementation session may therefore stop
at a CPython-tested patch pending an available PyPy runner, but PyPy validation
should be required before promotion, whether on another local runner or in
upstream CI.

## Compatibility, reliability, and performance

- **Compatibility:** no public API or telemetry schema changes.
- **Reliability:** teardown completes even if collection becomes eligible at
  the guard boundary; later tests no longer inherit poisoned global state.
- **Memory:** the local strong reference lasts only through one `remove()` call
  and does not retain engines after cleanup.
- **Concurrency:** resolving once closes a time-of-check/time-of-use lifetime
  race. The class-level mutable list remains out of scope because the report
  does not establish concurrent instrumentation calls.
- **Performance:** one weak-reference resolution replaces two; impact is
  negligible and favorable.
- **Observability:** no span shape changes. The fix prevents missing
  instrumentation caused by failed teardown/re-instrumentation.

## Human scope check

The user should explain in their own words that the proposed change:

- addresses the double weak-reference dereference shown by the traceback;
- retains a local target only for listener removal;
- includes a deterministic regression test plus PyPy validation; and
- intentionally does not change SQL-commenter log indexing.

Do not post this dossier verbatim or have an agent comment upstream.

## Stop conditions

- Stop until a human obtains maintainer agreement on the single-resolution
  lifecycle fix in the issue discussion.
- Stop if another contributor claims the issue or opens an overlapping PR.
- Do not start the patch while BuildKit #6966 occupies the single
  implementation slot.
