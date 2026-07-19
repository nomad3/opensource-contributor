# Prometheus Operator #8669 storage-mount reproducer

This reproducer tests the central runtime claim in
[prometheus-operator#8669](https://github.com/prometheus-operator/prometheus-operator/issues/8669):
that a PVC mounted with `subPath` on containerd/overlayfs receives writes in the
container snapshot instead of the persistent volume.

It deliberately isolates Kubernetes storage mounting from Prometheus Operator.
Two otherwise identical workloads mount static local volumes:

- `with-subpath` mounts `/prometheus` with `subPath: prometheus-db`;
- `without-subpath` mounts the volume root directly.

The test writes sentinels, captures the complete `/prometheus` mountinfo line,
checks the files from the Kubernetes node, restarts both pods, and checks the
sentinels again. An optional node-container restart approximates a node reboot.

## Run

Requirements: Docker Desktop, `kind`, and `kubectl`.

```bash
./run.sh
```

Include the optional node restart:

```bash
RUN_NODE_RESTART=1 ./run.sh
```

Preserve the cluster for inspection:

```bash
KEEP_CLUSTER=1 ./run.sh
```

The script creates only a dedicated kind cluster named `po-8669` by default.
It refuses to reuse an existing cluster so it cannot overwrite an unrelated
test environment. On success it deletes that cluster and restores the prior
kubectl context. On failure it preserves the cluster automatically so the
mounts and node paths remain available for diagnosis.

## Interpretation

An `overlay` filesystem type in the container is not, by itself, evidence that
writes bypass the volume. In kind, the Kubernetes node is a container and its
local storage can itself be backed by Docker overlayfs. The decisive evidence
is whether the same sentinel is visible:

1. from `/prometheus` in the workload;
2. from the node path backing the static volume;
3. after workload recreation;
4. after the optional node restart.

If this control passes but the Talos/local-path setup loses only the subpath
sentinel, collect the same complete mountinfo and node-path evidence there. That
would narrow the defect to the kubelet/containerd/provisioner combination
rather than the operator's YAML generation.
