# Control result: kind on Docker Desktop

Date: 2026-07-18

## Environment

```text
Docker client/server: 28.3.2
Docker storage driver: overlayfs
Docker driver status: io.containerd.snapshotter.v1
kind: v0.29.0
kind node image: kindest/node:v1.33.1
containerd in node: v2.1.1
kubelet in node: v1.33.1
kubectl client: v1.33.3 darwin/arm64
```

The reproducer was run with `RUN_NODE_RESTART=1`.

## Mount evidence

With `subPath: prometheus-db`:

```text
1357 1348 254:1 /docker/volumes/<volume-id>/_data/local/po-8669/with-subpath/prometheus-db /prometheus rw,relatime - ext4 /dev/vda1 rw,discard
```

Without a subpath:

```text
1325 1317 254:1 /docker/volumes/<volume-id>/_data/local/po-8669/without-subpath /prometheus rw,relatime - ext4 /dev/vda1 rw,discard
```

The Docker volume identifier is redacted because it is ephemeral and adds no
diagnostic value.

## Persistence evidence

Before workload restart, the sentinels were visible from the node:

```text
/var/local/po-8669/without-subpath/sentinel
without-subpath
/var/local/po-8669/with-subpath/prometheus-db/sentinel
with-subpath
```

The script explicitly asserted the expected content from both workload and node
paths. Both sentinels retained that content after:

1. a rolling restart of both deployments;
2. a restart of the `po-8669-control-plane` node container.

The script ended with:

```text
PASS: both storage layouts retained their sentinels
```

It then deleted the dedicated kind cluster.

## Conclusion

This control does not reproduce issue #8669. In this environment, containerd,
an overlayfs-backed Docker engine, and Kubernetes `subPath` correctly bind the
requested persistent-volume directory into `/prometheus`.

This result does **not** rule out a Talos, local-path provisioner, kubelet, or
containerd-version-specific defect. It narrows the next test to running the
same A/B comparison on the reporter's stack and comparing the complete
mountinfo root, mount point, filesystem, and source.

## Independent review

Claude Fable 5 initially found a blocking post-rollout pod-selection race and
two important assertion/wait weaknesses. After correction and a fresh
real-cluster run, its second adversarial review returned **GO** with no
remaining blocking or important findings.
