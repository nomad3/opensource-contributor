# Adversarial review prompt

Review the patch as a strict upstream maintainer. Do not edit files.

Look for:

- failure to solve the reported issue;
- tests that pass for the wrong reason;
- hidden behavior changes;
- concurrency, retry, reconciliation, or rollback defects;
- security regressions and unsafe defaults;
- platform, cloud, or Kubernetes-version assumptions;
- Helm install and upgrade incompatibility;
- missing observability;
- excessive scope;
- generated or temporary artifacts.

Classify findings as `BLOCKING`, `IMPORTANT`, or `OPTIONAL`. Do not recommend unrelated
cleanup. If there are no findings in a class, say so explicitly.
