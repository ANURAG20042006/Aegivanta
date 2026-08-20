# Aegivanta — Enterprise Production Deployment Guide

## 1. Prerequisites
- Kubernetes 1.28+ Cluster (EKS / GKE / AKS / On-Premises)
- PostgreSQL 15+ with SSL enabled
- Redis 7.2+ Cluster (Streams enabled)
- TLS 1.3 Ingress Controller

## 2. Helm Deployment
```bash
helm repo add aegivanta https://charts.aegivanta.io
helm upgrade --install aegivanta-core aegivanta/aegivanta-core \
  --namespace aegivanta-prod --create-namespace \
  --values values.production.yaml
```

## 3. Frontend Static Assets
Hosted via High-Availability CDN / Nginx container with Gzip & HTTP/2 enabled.
