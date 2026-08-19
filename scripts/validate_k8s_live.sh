#!/usr/bin/env bash
set -euo pipefail

echo "================================================================="
echo "      SentinelAI Live Kubernetes Server-Side Validation          "
echo "================================================================="

if ! command -v kubectl >/dev/null 2>&1; then
    echo "BLOCKED: kubectl unavailable — live Kubernetes schema validation not performed."
    exit 2
fi

echo "Checking Kubernetes Cluster Connectivity..."
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "BLOCKED: Kubernetes cluster unreachable."
    exit 2
fi

echo "Running Server-Side Dry-Run Validation on k8s/ manifests..."
kubectl apply --dry-run=server -f k8s/

echo "================================================================="
echo "RESULT: LIVE KUBERNETES SERVER-SIDE VALIDATION PASSED"
echo "================================================================="
