#!/usr/bin/env bash

set -euo pipefail

cluster_name="${CLUSTER_NAME:-po-8669}"
namespace="po-8669"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
keep_cluster="${KEEP_CLUSTER:-0}"
run_node_restart="${RUN_NODE_RESTART:-0}"
original_context="$(kubectl config current-context 2>/dev/null || true)"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: required command not found: $1" >&2
    exit 1
  fi
}

cleanup() {
  local status=$?

  if [[ "$status" -ne 0 ]]; then
    echo "test failed; preserving kind cluster for inspection: $cluster_name" >&2
    return
  fi

  if [[ "$keep_cluster" == "1" ]]; then
    echo "preserving kind cluster: $cluster_name"
    return
  fi

  kind delete cluster --name "$cluster_name"

  if [[ -n "$original_context" ]]; then
    kubectl config use-context "$original_context" >/dev/null
  fi
}

pod_name() {
  local names
  local count

  names="$(
    kubectl --context "kind-$cluster_name" -n "$namespace" \
      get pods -l "app=$1" \
      -o go-template='{{range .items}}{{if not .metadata.deletionTimestamp}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}'
  )"
  count="$(printf '%s\n' "$names" | awk 'NF { count++ } END { print count + 0 }')"

  if [[ "$count" -ne 1 ]]; then
    echo "error: expected one non-terminating pod for $1, found $count" >&2
    return 1
  fi

  printf '%s\n' "$names"
}

capture_case() {
  local workload="$1"
  local expected="$2"
  local actual
  local pod
  pod="$(pod_name "$workload")"

  echo "[$workload] mountinfo"
  # The awk program is intentionally evaluated in the container.
  # shellcheck disable=SC2016
  kubectl --context "kind-$cluster_name" -n "$namespace" exec "$pod" -- \
    awk '$5 == "/prometheus" { print }' /proc/self/mountinfo

  echo "[$workload] sentinel"
  actual="$(
    kubectl --context "kind-$cluster_name" -n "$namespace" exec "$pod" -- \
    cat /prometheus/sentinel
  )"

  if [[ "$actual" != "$expected" ]]; then
    echo "FAIL: $workload sentinel: expected '$expected', got '$actual'" >&2
    return 1
  fi

  echo "PASS: $workload sentinel contains '$actual'"
}

capture_node_sentinels() {
  local node="${cluster_name}-control-plane"
  local with_subpath
  local without_subpath

  with_subpath="$(
    docker exec "$node" \
      cat /var/local/po-8669/with-subpath/prometheus-db/sentinel
  )"
  without_subpath="$(
    docker exec "$node" \
      cat /var/local/po-8669/without-subpath/sentinel
  )"

  if [[ "$with_subpath" != "with-subpath" ]]; then
    echo "FAIL: node subpath sentinel: expected 'with-subpath', got '$with_subpath'" >&2
    return 1
  fi
  if [[ "$without_subpath" != "without-subpath" ]]; then
    echo "FAIL: node direct sentinel: expected 'without-subpath', got '$without_subpath'" >&2
    return 1
  fi

  echo "PASS: node paths contain both expected sentinels"
}

require_command docker
require_command kind
require_command kubectl

if ! docker info >/dev/null 2>&1; then
  echo "error: Docker daemon is not available" >&2
  exit 1
fi

if kind get clusters | grep -Fxq "$cluster_name"; then
  echo "error: kind cluster already exists: $cluster_name" >&2
  echo "choose CLUSTER_NAME or delete the existing cluster explicitly" >&2
  exit 1
fi

trap cleanup EXIT

echo "[environment]"
docker version --format 'docker client={{.Client.Version}} server={{.Server.Version}}'
docker info --format 'docker storage driver={{.Driver}} status={{.DriverStatus}}'
kind version
kubectl version --client

kind create cluster --name "$cluster_name" --wait 120s
docker exec "${cluster_name}-control-plane" containerd --version
docker exec "${cluster_name}-control-plane" kubelet --version

kubectl --context "kind-$cluster_name" apply -f "$script_dir/manifests.yaml"
kubectl --context "kind-$cluster_name" -n "$namespace" \
  rollout status deployment/with-subpath --timeout=120s
kubectl --context "kind-$cluster_name" -n "$namespace" \
  rollout status deployment/without-subpath --timeout=120s

with_subpath_pod="$(pod_name with-subpath)"
without_subpath_pod="$(pod_name without-subpath)"

kubectl --context "kind-$cluster_name" -n "$namespace" exec "$with_subpath_pod" -- \
  sh -c 'printf "%s\n" with-subpath > /prometheus/sentinel'
kubectl --context "kind-$cluster_name" -n "$namespace" exec "$without_subpath_pod" -- \
  sh -c 'printf "%s\n" without-subpath > /prometheus/sentinel'

capture_case with-subpath with-subpath
capture_case without-subpath without-subpath

echo "[node] persisted files before pod restart"
docker exec "${cluster_name}-control-plane" \
  find /var/local/po-8669 -type f -name sentinel -print -exec cat {} \;
capture_node_sentinels

kubectl --context "kind-$cluster_name" -n "$namespace" \
  rollout restart deployment/with-subpath deployment/without-subpath
kubectl --context "kind-$cluster_name" -n "$namespace" \
  rollout status deployment/with-subpath --timeout=120s
kubectl --context "kind-$cluster_name" -n "$namespace" \
  rollout status deployment/without-subpath --timeout=120s

echo "[workloads] persisted files after pod restart"
capture_case with-subpath with-subpath
capture_case without-subpath without-subpath
capture_node_sentinels

if [[ "$run_node_restart" == "1" ]]; then
  echo "[node] restarting ${cluster_name}-control-plane"
  docker restart "${cluster_name}-control-plane" >/dev/null

  for _ in {1..60}; do
    if kubectl --context "kind-$cluster_name" get nodes >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done

  kubectl --context "kind-$cluster_name" wait \
    --for=condition=Ready node/"${cluster_name}-control-plane" --timeout=120s
  kubectl --context "kind-$cluster_name" -n "$namespace" \
    rollout status deployment/with-subpath --timeout=120s
  kubectl --context "kind-$cluster_name" -n "$namespace" \
    rollout status deployment/without-subpath --timeout=120s

  echo "[workloads] persisted files after node restart"
  capture_case with-subpath with-subpath
  capture_case without-subpath without-subpath
  capture_node_sentinels
fi

echo "PASS: both storage layouts retained their sentinels"
