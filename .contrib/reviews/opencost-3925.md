# Maintainer review: OpenCost PR #3925

## Verdict

**DO NOT PROMOTE.**

The map-swap approach fixes the reported empty/partial-read window, but the
new duplicate-watch guard can deadlock `KubernetesClusterCacheV2.Run()`. The
current head also has no regression tests, is not gofmt-clean, has no executed
Build/Test or Format Check workflow, and fails the DCO gate.

This is a private, read-only review artifact. No GitHub comment or review was
posted.

## Pull request state

- PR: [opencost/opencost#3925](https://github.com/opencost/opencost/pull/3925)
- Issue: [#3924](https://github.com/opencost/opencost/issues/3924)
- Base: `develop`
- Head: `cd4b4217db060ab74a5dd1e1707362ae20915571`
- Refreshed: 2026-07-19T03:41:58Z
- State: open, non-draft, review required
- Mergeability: mergeable; merge-state status: behind
- Branch relation: 5 commits ahead and 3 commits behind `develop`
- Human maintainer approvals: none
- Files changed: one production file; no test files

## What is correct

The original `Replace()` made the store observably inconsistent:

1. replace `s.items` with an empty map under the write lock;
2. release the lock; and
3. call `Add()` once per item, locking separately for every write.

Readers could therefore observe an empty or partially reconstructed cache.

The current head builds `newItems` without exposing it, then swaps the map
under one write lock. A concurrent `GetAll()` observes either the old map or
the complete new map. Transform work also happens outside the critical
section, avoiding long reader stalls. Capturing and clearing `onInit` under the
same lock and invoking it after unlock avoids callback-under-lock deadlocks.

Moving transform work outside the lock also retains the old snapshot if a type
assertion or transform panics, rather than leaving an empty store or a locked
mutex.

## BLOCKING

### 1. Duplicate `Watch()` can deadlock `Run()`

The patch adds:

```go
if s.isWatching {
    s.mutex.Unlock()
    return
}
```

`KubernetesClusterCacheV2.Run()` creates a fresh wait group, adds 16, and calls
each store's `Watch(stopCh, wg.Done)`, then waits. If `Run()` is invoked again
or concurrently while the stores are already watching, every `Watch()` silently
returns without invoking the supplied `wg.Done` callback. The second `Run()`
then waits forever.

After `Stop()`, `isWatching` is also never reset. A later `Run()` has the same
wait-group deadlock, in addition to the existing lifecycle question around the
closed/nil stop channel.

The maintainer requested restricting additional calls “while already
watching,” not silently violating the caller's initialization-callback
contract. The implementation needs an explicit lifecycle design:

- reject duplicate `Run()`/`Watch()` with a returned status or error that the
  caller handles;
- make duplicate `Watch()` satisfy the supplied initialization callback when
  initialization is already complete; or
- put the single-run guard at `KubernetesClusterCacheV2.Run()` and ensure it
  cannot wait on callbacks that will never execute.

Do not merge the silent-return behavior without a deterministic duplicate-run
test.

### 2. No regression or concurrency tests

The PR changes atomic visibility, callback synchronization, and watch
lifecycle but adds no tests. The claimed package test pass only proves existing
coverage did not fail; it does not demonstrate the reported race is fixed.

Required focused tests:

1. seed an old complete snapshot;
2. block `transformFunc` during a replacement;
3. call `GetAll()` while replacement is in progress and prove it returns the
   complete old snapshot, never empty or partial;
4. release the transform and prove readers receive the complete new snapshot;
5. prove `onInit` is invoked exactly once and outside the store lock;
6. exercise duplicate/concurrent `Watch()` or `Run()` without hanging; and
7. run the tests under `-race`.

### 3. Current head is neither formatted nor validated

The diff contains three added blank lines with trailing tab characters. The
three substantive pull-request workflows did not execute:

| Workflow | Conclusion | Jobs |
| --- | --- | ---: |
| Build/Test | `action_required` | 0 |
| Format Check | `action_required` | 0 |
| Generate SBOM | `action_required` | 0 |

The green integration wrapper ran permission/no-op jobs; image creation and
all substantive integration jobs were skipped. DCO is also
`ACTION_REQUIRED`, and Snyk reports an error state.

Before promotion, clean the head and run:

```bash
go fmt ./...
git diff --check
go vet ./...
go test -race ./pkg/clustercache/... -count=1
just test
```

Then authorize and execute the real Build/Test, Format Check, and SBOM
workflows on the final head, and resolve DCO.

## IMPORTANT

### Clarify write ordering during off-lock snapshot construction

Building the replacement map outside the lock is the right reader-latency
tradeoff, but it allows `Add`, `Update`, or `Delete` to complete before the
swap and then be overwritten by the replacement snapshot. Overlapping
operations can be linearized with `Replace` after those writes, so this is not
automatically incorrect. Still, the expected client-go `Store`/Reflector
ordering should be documented or tested so future callers do not assume that
every concurrent mutation survives a replace.

It also changes the synchronization contract for `transformFunc`: `Add()` and
`Update()` invoke it while holding `s.mutex`, while the new `Replace()` invokes
it outside that mutex. An external concurrent `Add()` or `Update()` can now run
the same arbitrary transform concurrently with replacement. Built-in
transforms appear intended to be pure and a Reflector normally serializes its
own store callbacks, so this is not automatically a defect. The generic store
contract should nevertheless document transform concurrency or add a test
using a transform that detects overlapping calls.

### Rebase and rerun on current `develop`

The branch is three commits behind. Recheck lifecycle behavior, regenerate the
diff, and run all gates after updating; current source review does not validate
the eventual merge result.

## OPTIONAL

- Replace the anonymous immediately invoked function around lock/swap with a
  small named helper or explicit lock/unlock after tests establish the
  no-panic critical section. The current shape adds indentation without
  providing meaningful panic safety because the operations under lock are map
  assignment and function-field reads/writes.
- Add a short comment stating the map assignment is the `Replace`
  linearization point.
- Update the PR description: it still says the lock is held through the entire
  clear-and-repopulate operation, but current head builds off-lock and swaps
  under lock.
- Record that the current Snyk error is quota exhaustion (“used your limit of
  private tests”), not evidence of a dependency vulnerability.

## Promotion checklist

- [ ] Define duplicate/restart watch lifecycle without a wait-group deadlock.
- [ ] Add deterministic atomic-snapshot tests.
- [ ] Add initialization-callback and duplicate-watch tests.
- [ ] Pass `go test -race ./pkg/clustercache/...`.
- [ ] Remove trailing whitespace with `go fmt ./...`.
- [ ] Update against current `develop`.
- [ ] Execute Build/Test and Format Check with real jobs.
- [ ] Resolve DCO and explain or resolve Snyk.
- [ ] Obtain human maintainer approval.
