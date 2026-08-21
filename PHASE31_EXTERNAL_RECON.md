# PHASE 31 — EXTERNAL RECONNAISSANCE & PORT SCANNING SPECIFICATION

## 1. Monitored Sensitive Ports

- **Port 3389 (RDP)**: Critical remote desktop exposure risk.
- **Port 22 (SSH)**: Public administrative shell exposure risk.
- **Port 6443 (Kubernetes API)**: Public cluster control plane exposure.
- **Port 6379 (Redis)**: Unauthenticated in-memory cache exposure.
- **Port 9200 (Elasticsearch)**: Unindexed enterprise search exposure.
- **Port 27017 (MongoDB)**: Unauthenticated database instance risk.
