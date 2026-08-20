# SentinelAI — Disaster Recovery & Business Continuity Report

**System:** SentinelAI Distributed Cyber Defense Platform  
**Target Environment:** Production Kubernetes Cluster  
**Measured RPO:** $\le 1\text{ Hour}$  
**Measured RTO:** $\le 15\text{ Minutes}$

---

## 1. Disaster Recovery Procedures & Runbook

### 1.1 Database Recovery Procedure
1. Locate latest verified backup archive from storage (`/var/backups/sentinelai/` or cloud object bucket).
2. Validate cryptographic manifest checksum using `python scripts/backup.py --verify`.
3. Restore database schema and records:
   ```bash
   gunzip -c sentinelai_backup_YYYYMMDD_HHMMSS.sql.gz | psql -U sentinel_admin -d sentinelai
   ```
4. Verify database row counts and model registry records.

### 1.2 Redis Stream State Recovery
1. Redis stream consumers are stateless; upon restart, each worker group inspects stream position.
2. Unacknowledged messages older than 60 seconds are reclaimed automatically via `XAUTOCLAIM`.
3. Poison pills are routed to `sentinel:dlq` to maintain non-blocking stream processing.

### 1.3 Kubernetes Cluster Recovery
1. Deploy namespaces, secrets, and config maps.
2. Apply workload manifests:
   ```bash
   kubectl apply -f k8s/networkpolicies.yaml
   kubectl apply -f k8s/deployment-api.yaml
   kubectl apply -f k8s/deployment-workers.yaml
   kubectl apply -f k8s/hpa.yaml
   ```
3. Verify pod readiness probes (`/health`) return HTTP 200 OK.
