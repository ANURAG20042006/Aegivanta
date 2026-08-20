# AEGIVANTA — OPERATIONS & RUNBOOK GUIDE

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  

---

## 1. Routine Operational Procedures

### A. Health Monitoring & Observability
- **Liveness Probe**: `GET /api/v1/health` (Checks gateway worker process).
- **Readiness Probe**: `GET /api/v1/health/ready` (Validates PostgreSQL database connection, Redis stream broker, and model artifact SHA256 integrity).
- **Prometheus Metrics**: `GET /metrics` (Exposes `aegivanta_*` counters and gauges).

### B. Redis Stream Management & DLQ Maintenance
- **List Dead Letter Queue entries**:
  ```python
  from backend.app.services.distributed_stream_service import distributed_stream_engine
  entries = await distributed_stream_engine.backend.list_dlq("aegivanta:telemetry:dlq", count=20)
  ```
- **Replay DLQ message**:
  ```python
  res = await distributed_stream_engine.replay_dlq_event(dlq_message_id="1787225424540-0")
  ```

---

## 2. Model Governance & Safe Rollback

### A. Candidate Model Benchmark Evaluation
1. Retrain pipeline generates new candidate artifact in `ml/artifacts/candidate_model.joblib`.
2. Evaluate 5-fold cross-validation F1 score and False Positive Rate (FPR):
   - Promotion gate rule: Candidate `macro_f1 >= champion_macro_f1` AND `fpr <= 0.01`.
3. If criteria met, promote candidate to active status in `ModelRegistry` database table.

### B. Emergency Model Rollback
If inference anomalies occur:
```bash
python scripts/rollback_model.py --version catboost-v1.0 --verify-sha256
```
The rollback engine automatically verifies the original SHA-256 hash before restoring the champion artifact.
