# Aegivanta — Disaster Recovery & Business Continuity Plan

## 1. Recovery Objectives
- **RPO (Recovery Point Objective)**: < 5 minutes (WAL archiving & streaming replication).
- **RTO (Recovery Time Objective)**: < 15 minutes (Automated container redeployment & database restore).

## 2. Tested Failure Scenarios
1. PostgreSQL Primary Node Failure -> Automatic replica promotion.
2. Redis Cluster Partition -> Consumer group auto-reconnection via `XAUTOCLAIM`.
3. Kubernetes Node Eviction -> Pod Disruption Budgets & Horizontal Pod Autoscaling.
