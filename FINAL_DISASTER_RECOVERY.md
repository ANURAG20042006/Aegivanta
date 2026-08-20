# SentinelAI — Final Disaster Recovery & Business Continuity Specification

## 1. Objectives & Metrics

- **Maximum Tolerable Downtime (MTD)**: 1 hour
- **Recovery Point Objective (RPO)**: $\le 1$ hour
- **Recovery Time Objective (RTO)**: $\le 15$ minutes

---

## 2. Recovery Plan Matrix

| Failure Mode | Impact | Automatic Recovery | Manual Procedure |
| :--- | :--- | :--- | :--- |
| **API Pod Crash** | Transient HTTP 502/503 | K8s replaces pod; traffic shifts to healthy pods in $\le 2\text{ s}$ | None required |
| **Worker Node Failure** | Temporary stream lag | K8s reschedules pods; Redis `XAUTOCLAIM` reclaims pending messages | Verify stream lag clears |
| **Redis Crash / Restart** | Stream temporarily paused | Redis restarts from AOF/RDB; workers reconnect with exponential backoff | None required |
| **Database Corruption** | API/Workers lose persistence | None | Restore from latest verified `.sql.gz` backup manifest via `scripts/backup.py` |
| **Cluster Total Loss** | Platform outage | None | Run Terraform/Helm deployment against disaster recovery cluster and restore DB backup |
