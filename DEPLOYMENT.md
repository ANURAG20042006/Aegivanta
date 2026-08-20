# AEGIVANTA — ENTERPRISE DEPLOYMENT GUIDE

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  

---

## 1. Quickstart Local Deployment (Docker Compose)

### Prerequisites
- Docker Engine 24.0+ & Docker Compose v2
- 4 CPU cores, 8 GB RAM minimum

### Launch Commands
```bash
# 1. Clone repository
git clone https://github.com/ANURAG20042006/SENTINELAI.git aegivanta
cd aegivanta

# 2. Configure environment
cp .env.example .env

# 3. Launch full stack (Backend, Frontend, PostgreSQL, Redis)
docker compose -f docker/docker-compose.yml up -d --build

# 4. Verify cluster health
curl -f http://localhost/health
```

Access Interfaces:
- **Commercial SOC Interface**: [http://localhost](http://localhost)
- **FastAPI OpenAPI Documentation**: [http://localhost/docs](http://localhost/docs)
- **Default Credentials**: `admin` / `Admin_Secure2026!`

---

## 2. Production Kubernetes Cluster Deployment

### Prerequisites
- Kubernetes v1.28+ cluster (EKS, GKE, AKS, or bare-metal K8s)
- `kubectl` configured with cluster-admin permissions
- Ingress-NGINX Controller with TLS support

### Step-by-Step Deployment
```bash
# 1. Create dedicated Namespace
kubectl apply -f k8s/namespace.yaml

# 2. Deploy ServiceAccount and RBAC
kubectl apply -f k8s/serviceaccount.yaml

# 3. Provision Secrets (Inject Vault/KMS passwords)
kubectl apply -f k8s/secret-template.yaml

# 4. Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# 5. Launch Redis Distributed Broker
kubectl apply -f k8s/redis.yaml

# 6. Launch API Server & Stream Workers
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/service-api.yaml

# 7. Apply Ingress, HPA, PDB, and NetworkPolicy
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/pdb.yaml
kubectl apply -f k8s/networkpolicy.yaml
```

### Static Verification
```bash
python scripts/validate_k8s_manifests.py
```
Expected output:
`RESULT: ALL KUBERNETES MANIFESTS PASSED STRICT VALIDATION (0 ERRORS)`
