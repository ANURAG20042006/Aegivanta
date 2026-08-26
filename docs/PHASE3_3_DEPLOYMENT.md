# SENTINELAI — PHASE 3.3 PRODUCTION KUBERNETES DEPLOYMENT GUIDE
================================================================

## 1. Deployment Topology & Verification Status

```mermaid
graph TD
    User([SOC Analyst / Ingestion Stream]) -->|HTTPS / TLS| Ingress[NGINX Ingress Controller]
    Ingress -->|ClusterIP:8000| ServiceAPI[Service: sentinelai-api]
    ServiceAPI --> PodAPI1[API Pod 1]
    ServiceAPI --> PodAPI2[API Pod 2]
    
    PodAPI1 -->|Ingest Stream Events| RedisCluster[(Redis Streams Broker)]
    PodAPI2 -->|Ingest Stream Events| RedisCluster
    
    RedisCluster -->|XREADGROUP| Worker1[Worker Pod 1: ML Inference]
    RedisCluster -->|XREADGROUP| Worker2[Worker Pod 2: ML Inference]
    
    Worker1 -->|Store Alerts/Incidents| PostgresDB[(PostgreSQL Primary)]
    Worker2 -->|Store Alerts/Incidents| PostgresDB
    
    Worker1 -->|Publish Threat| PubSub[(Redis PubSub)]
    PubSub --> PodAPI1
    PubSub --> PodAPI2
```

### Component Status Matrix:
- **Static Manifest Validation**: `VERIFIED STATICALLY` (via `scripts/validate_k8s_manifests.py`)
- **Container Hardening (Non-Root UID 10001, Cap Drop ALL)**: `VERIFIED STATICALLY & LOCALLY`
- **Fail-Closed API Readiness Check**: `VERIFIED LOCALLY` (via `scripts/verify_api_readiness_behavior.py`)
- **Worker Graceful Shutdown & XAUTOCLAIM Recovery**: `VERIFIED WITH SIMULATION` (via `scripts/verify_worker_shutdown_and_recovery.py`)
- **Kubectl Server-Side Dry-Run**: `BLOCKED BY ENVIRONMENT` (kubectl CLI not installed on host)
- **Live Ingress & TLS**: `BLOCKED BY ENVIRONMENT` (No live Ingress Controller present on host)
- **Live HPA Metrics Scaling**: `BLOCKED BY ENVIRONMENT` (metrics-server not present on host)

---

## 2. Deployment Commands

### Local Offline Manifest Validation
```bash
python scripts/validate_k8s_manifests.py
```

### Live Kubernetes Cluster Deployment (when cluster is configured)
```bash
# 1. Namespace & ServiceAccount
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/serviceaccount.yaml

# 2. ConfigMap & Secrets (replace placeholders with KMS/Vault values)
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret-template.yaml

# 3. Redis StatefulSet & NetworkPolicy
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/networkpolicy.yaml

# 4. API, Workers, Autoscalers & Ingress
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/service-api.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/pdb.yaml
kubectl apply -f k8s/ingress.yaml
```

### Live Cluster Health Inspection
```bash
python scripts/validate_phase3_3_cluster.py
```

### Rollback Procedure
```bash
kubectl rollout undo deployment/sentinelai-api -n sentinelai
kubectl rollout undo deployment/sentinelai-worker -n sentinelai
```
