# Aegivanta — Enterprise Production Deployment Guide (v25.0.0)

## 1. System Requirements & Prerequisites
- **Kubernetes**: v1.28+ Cluster (EKS / GKE / AKS / On-Premises Bare-Metal)
- **Database**: PostgreSQL 15+ (Multi-Tenant Schemas, SSL/TLS enabled, connection pooling)
- **Cache & Message Broker**: Redis 7.2+ Cluster with Streams enabled
- **Ingress & Security**: TLS 1.3 Ingress Controller with WAF & Rate Limiting
- **Node Resources**: Minimum 4 Nodes, 8 vCPU, 32GB RAM per worker node

## 2. Production Helm Deployment
```bash
# 1. Add Aegivanta Helm repository
helm repo add aegivanta https://charts.aegivanta.io
helm repo update

# 2. Deploy core platform stack
helm upgrade --install aegivanta-core aegivanta/aegivanta-core \
  --namespace aegivanta-prod --create-namespace \
  --values values.production.yaml \
  --set global.environment=production \
  --set global.projectVersion=25.0.0

# 3. Verify rollout status
kubectl rollout status deployment/aegivanta-backend -n aegivanta-prod
kubectl rollout status deployment/aegivanta-workers -n aegivanta-prod
```

## 3. Frontend & CDN Deployment
- Production assets built via `npm run build` (Vite + React 18).
- Deployed to Edge CDN / High-Availability Nginx pods with HTTP/2, Gzip, and strict CSP headers.
