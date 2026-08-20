# SentinelAI — Final Operations & SRE Runbook

## Routine Operations & Incident Procedures

### 1. Health Monitoring & Alerts

| Alert | Condition | Action Procedure |
| :--- | :--- | :--- |
| `HIGH_STREAM_LAG` | Redis stream pending items $> 5,000$ | Verify worker pod health; scale worker replicas via HPA or `kubectl scale`. |
| `FREQUENT_DLQ` | Messages entering `sentinel:dlq` | Inspect DLQ payload for malformed PCAP or unsupported protocol schemas. |
| `FEED_SYNC_FAILURE` | External TI feed offline $> 3$ intervals | Check egress network policy, API token validity, or feed provider status. |
| `MODEL_DRIFT_ALERT` | PSI $> 0.25$ on feature streams | Review drift report; analyze feedback queue; evaluate candidate model in Staging. |

---

### 2. Routine Maintenance Procedures

#### 2.1 Generating Automated Backups
```bash
python scripts/backup.py --backup-dir /var/backups/sentinelai
```

#### 2.2 Verifying Cryptographic Audit Log Chains
```python
from backend.app.services.immutable_audit_service import ImmutableAuditService

is_valid = await ImmutableAuditService.verify_chain_integrity(db_session)
print(f"Audit log tamper verification: {is_valid}")
```

#### 2.3 Rolling Restarts of API & Worker Deployments
```bash
kubectl rollout restart deployment sentinelai-api -n sentinelai
kubectl rollout restart deployment sentinelai-worker-detection -n sentinelai
kubectl rollout status deployment sentinelai-api -n sentinelai
```
