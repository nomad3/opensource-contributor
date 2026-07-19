# Handoff — Tekton Pipeline #4426

## Objective

Add real-cluster integration coverage for the four generated TaskRun debug
scripts.

## Completed

- Verified the issue is unassigned, maintainer-reactivated, and has no
  overlapping pull request.
- Read repository agent, development, test, debug, and PR instructions.
- Added a table-driven e2e test covering all four script outcomes.
- Avoided new module/vendor dependencies by following the existing
  `kubectl`-based e2e pattern.
- Created signed-off local commit `895bd19ca`.
- Exported the commit as `.contrib/patches/tekton-4426-debug-scripts.patch`.

## Evidence

```text
go test -tags=e2e ./test -run '^$'
ok github.com/tektoncd/pipeline/test [no tests to run]

go test ./pkg/pod ./pkg/entrypoint
ok github.com/tektoncd/pipeline/pkg/pod
ok github.com/tektoncd/pipeline/pkg/entrypoint

./hack/verify-agent-readiness.sh
agent readiness checks passed

git diff --check
clean
```

## Remaining validation

Run the actual e2e test on a disposable cluster with the current Tekton source
build and alpha API fields enabled:

```text
go test -v -count=1 -tags=e2e -timeout=20m ./test -run '^TestTaskRunDebugScripts$'
```

The laptop has `docker`, `kind`, and `kubectl`, but Docker did not return a
server response and `ko` is not installed. No cluster or registry setup was
performed.

## Next exact action

Apply the exported patch to a fresh Tekton checkout, run the real-cluster test,
then resume adversarial review. Do not open an upstream PR until all four cases
pass.

## Do not do

- Do not add `k8s.io/client-go/tools/remotecommand`; Tekton's vendor tree does
  not contain it.
- Do not open a PR based only on compile-time validation.
- Do not claim issue ownership until work resumes.
