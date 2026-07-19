# Prometheus Operator issue #8669 reconnaissance

- Issue: <https://github.com/prometheus-operator/prometheus-operator/issues/8669>
- Reported impact: silent Prometheus TSDB loss after node reboot
- Status checked: 2026-07-19
- Ownership: unassigned
- Overlapping pull request: none found
- Recommendation: **investigate before implementation**

## Why it is urgent

If reproduced, the report describes total, silent loss of retained monitoring
data. That is a high-severity observability and incident-response failure.

## Important source finding

The report says there is no API for disabling the generated storage `subPath`.
Prometheus Operator v0.90.1—the version named in the report—already exposes:

```yaml
prometheus:
  prometheusSpec:
    storageSpec:
      disableMountSubPath: true
      volumeClaimTemplate:
        spec:
          storageClassName: local-path
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 50Gi
```

Evidence at tag `v0.90.1`:

- `StorageSpec.DisableMountSubPath` is serialized as
  `disableMountSubPath`.
- `SubPathForStorage()` returns an empty subpath when that field is true.
- kube-prometheus-stack passes `prometheusSpec.storageSpec` directly into the
  generated Prometheus custom resource.

The field is marked deprecated because the operator intends to remove subpath
usage in a future release, but it is currently implemented.

## Why a code patch is premature

The claim that a Kubernetes `subPath` PVC mount becomes the container's
overlayfs writable layer is not yet backed by a minimal public reproducer or
complete mount evidence. The issue includes a shortened mountinfo fragment but
not the mount point, mount IDs, root, source, or the corresponding kubelet and
containerd mount chain. Removing subpath globally could also alter established
storage layouts and upgrade behavior.

## Smallest useful next artifact

Reproduce on a disposable Talos or containerd cluster with two otherwise
identical Prometheus resources:

1. default storage behavior;
2. `disableMountSubPath: true`.

For each case capture:

- rendered Prometheus CR and StatefulSet;
- `/proc/self/mountinfo` from the Prometheus container, filtered by the exact
  `/prometheus` mount point without truncation;
- `findmnt -T /prometheus -o TARGET,SOURCE,FSTYPE,OPTIONS`;
- a sentinel file written under `/prometheus`;
- the host/PV path before and after pod restart and node reboot;
- containerd and kubelet versions plus snapshotter and storage class details.

The comparison will distinguish an operator bug from a kubelet, containerd,
Talos, or local-path provisioner interaction.

## Draft upstream comment

> This looks high impact, so I checked the reported v0.90.1 source before
> proposing a storage API change. That version already has
> `spec.storage.disableMountSubPath`; when true, `SubPathForStorage()` emits an
> empty subpath. kube-prometheus-stack passes
> `prometheus.prometheusSpec.storageSpec` through to that field, so the
> immediate comparison configuration should be:
>
> ```yaml
> prometheus:
>   prometheusSpec:
>     storageSpec:
>       disableMountSubPath: true
>       volumeClaimTemplate:
>         # existing PVC template
> ```
>
> Could you compare the default and disabled-subpath cases and attach the full
> `/proc/self/mountinfo` line for `/prometheus` (including mount point, root,
> source, and options), plus the containerd snapshotter and local-path
> provisioner versions? The current shortened overlay line does not establish
> that `/prometheus` itself is the overlay mount. If the A/B test reproduces
> data loss only with subpath enabled, that would give us a safe regression
> target without guessing at a broad storage-layout change.

