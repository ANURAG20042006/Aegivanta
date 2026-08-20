# SentinelAI — Final Production Deployment Guide

## Prerequisites & Requirements

- **Kubernetes Cluster**: v1.28+ (e.g. Minikube, EKS, GKE, AKS) with Metrics Server enabled.
- **PostgreSQL**: v15+ database cluster.
- **Redis**: v7+ with persistence (AOF/RDB) and Streams support.
- **Node.js**: v18+ (for frontend assets).
- **Python**: 3.11+.

---

## 1. Step-by-Step Production Deployment

### Step 1: Namespace & Secrets Setup
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
```

### Step 2: Database Initialization & Migrations
```bash
python scripts/verify_environment.py
```

### Step 3: Network Policies & RBAC
```bash
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/networkpolicies.yaml
```

### Step 4: Workload Deployment
```bash
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-workers.yaml
kubectl apply -f k8s/pdb.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

### Step 5: Verification & Readiness Checks
```bash
kubectl get pods -n sentinelai
python scripts/validate_k8s_manifests.py
python scripts/validate_k8s_live.py
```
