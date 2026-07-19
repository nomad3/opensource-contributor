# Maintainer review: MCP Python SDK PR #3127

- Repository: `modelcontextprotocol/python-sdk`
- Pull request: <https://github.com/modelcontextprotocol/python-sdk/pull/3127>
- Issue: <https://github.com/modelcontextprotocol/python-sdk/issues/3126>
- Reviewed head: `64bfa6112dd5354339c10f19be245f735aa5fe56`
- Review mode: read-only; no upstream comment, review, or code change
- Verdict: **PROMOTABLE AFTER WORDING CLARIFICATION AND HUMAN APPROVAL**

## Summary

The patch correctly prevents each dispatcher from minting a numeric request ID at
or below the greatest caller-supplied numeric ID it has observed. It applies the
same rule to `JSONRPCDispatcher` and `DirectDispatcher`, handles numeric strings
through the existing request-ID coercion, and has comprehensive green CI.

The remaining concern is wording and follow-up scope, not the mechanics of that
fix. The repository's protocol requirement says request IDs are never reused
within a session, while
the current implementation and an existing test deliberately allow a caller to
reuse an ID after its earlier request completes. The pull request fixes one way
the dispatcher can reuse an ID, but it does not establish the broader invariant
suggested by some of its comments and by the protocol requirement.

## Important: narrow the invariant claim

The following sequence remains accepted:

1. The dispatcher mints request ID `1` and that request completes.
2. A caller submits a later request with `request_id=1`.
3. Because `1` is no longer pending, the later request is sent with the same
   wire ID.

The equivalent reuse is also possible when a caller supplies the same completed
opaque string ID twice. Existing coverage in
`test_send_raw_request_with_in_flight_request_id_raises_and_frees_id_on_completion`
explicitly asserts that an ID becomes reusable after completion.

That behavior conflicts with `protocol:request-id:unique` in
`tests/interaction/_requirements.py`, which describes IDs as never reused within
the session, and with the MCP requirement that a requestor must not previously
have used the ID in the same session.

This does not make the bounded counter-advance change incomplete for the issue it
claims to fix. The issue and pull request explicitly select the incremental
scope, and the implementation satisfies that contract. Comments that say IDs
are generally single-use within a session should nevertheless be narrowed: the
implemented guarantee is that future minted numeric IDs advance past
caller-supplied numeric IDs.

The broader caller-reuse behavior is a pre-existing protocol-conformance gap
worth tracking separately, not a prerequisite for merging this improvement. A
full solution would need session-lifetime tracking of IDs actually issued,
concurrency-safe reservation, and rollback when a request is proven never to
have been issued.

## Important considerations

- A very large caller-supplied integer permanently advances `_next_id` to that
  value. Request IDs are opaque, so this is probably compatible, but the
  behavior should be intentional because every later minted ID inherits that
  jump.
- Tests establish the primary regression for integer and numeric-string IDs.
  If the full invariant is selected, add completed-ID reuse tests rather than
  only in-flight collision tests.

## What is good

- The counter is advanced synchronously before the first await, so the proposed
  state transition does not introduce an async scheduling race.
- Numeric strings and integers share the existing normalized collision domain.
- The two dispatcher implementations remain behaviorally aligned.
- The regression tests exercise the intended minted sequence and the full
  Python/platform CI matrix is green.
- The patch is small and avoids unrelated refactoring.

## Exact promotion boundary

Promote only after:

1. Broad comments about all IDs being single-use are narrowed to the actual
   minted-versus-supplied numeric guarantee, or clearly presented only as the
   protocol rationale.
2. The pull request receives the required human approval.

The present implementation is a reasonable small incremental fix. The
session-lifetime reuse cases above should be tracked independently if the
project wants the dispatcher to enforce the broader protocol requirement.
