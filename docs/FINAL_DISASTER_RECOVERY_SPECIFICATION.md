# Aegivanta — Disaster Recovery & Business Continuity Plan (v25.0.0)

## 1. Recovery Objectives (SLO Validated)
- **RPO (Recovery Point Objective)**: < 5 minutes (continuous WAL archiving & streaming replication).
- **RTO (Recovery Time Objective)**: < 15 minutes (automated Kubernetes redeployment & database failover).

## 2. Tested Failure & Recovery Procedures
1. **Database Failover**: Automated Patroni/RDS replica promotion with zero data loss.
2. **Redis Partition Recovery**: Consumer group re-attachment and message recovery via `XAUTOCLAIM`.
3. **Worker Failover**: Kubernetes Horizontal Pod Autoscaler (HPA) and Pod Disruption Budgets (PDB).
4. **Tenant Data Recovery**: Point-in-time recovery (PITR) per tenant schema without global downtime.
5. **Connector & Webhook Recovery**: Automatic exponential retry with jitter and dead-letter queue (DLQ) re-drive.
