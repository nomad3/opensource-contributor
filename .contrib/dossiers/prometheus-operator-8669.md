# Prometheus Operator issue #8669 reconnaissance

- Issue: <https://github.com/prometheus-operator/prometheus-operator/issues/8669>
- Reported impact: silent Prometheus TSDB loss after node reboot
- Status checked: 2026-07-18
- Ownership: unassigned
- Overlapping pull request: none found
- Recommendation: **investigate before implementation**

## Control reproduction result

A reusable reproducer now exists under
`reproducers/prometheus-operator-8669/`. It was executed with an optional node
restart on a Kubernetes v1.33.1 node created by kind v0.29.0, using Docker
28.3.2 with the containerd image store and overlayfs.

Both the direct and `subPath: prometheus-db` mounts:

- resolved to ext4-backed `/dev/vda1` mounts at `/prometheus`;
- exposed their sentinels at the corresponding node paths;
- retained the expected content after pod recreation;
- retained the expected content after the kind node container restarted.

Result:

```text
PASS: both storage layouts retained their sentinels
```

Full evidence and interpretation:
`reproducers/prometheus-operator-8669/result-kind-docker-desktop.md`.

This control contradicts the broad claim that containerd plus overlayfs always
redirects a Kubernetes subpath mount into an ephemeral container snapshot. It
does not contradict a narrower Talos/local-path/version-specific defect.

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
> I also ran a control A/B test on kind with Docker's containerd image store:
> both layouts were node-visible and survived pod plus node-container restarts.
> Could you compare the default and disabled-subpath cases and attach the full
> `/proc/self/mountinfo` line for `/prometheus` (including mount point, root,
> source, and options), plus the containerd snapshotter and local-path
> provisioner versions? The current shortened overlay line does not establish
> that `/prometheus` itself is the overlay mount. If the A/B test reproduces
> data loss only with subpath enabled, that would give us a safe regression
> target without guessing at a broad storage-layout change.
