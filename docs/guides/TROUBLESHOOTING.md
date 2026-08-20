# AEGIVANTA — TROUBLESHOOTING & INCIDENT DIAGNOSTICS

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  

---

## 1. Common Diagnostics & Resolutions

### Symptom 1: HTTP 503 / Database Connectivity Failure
- **Root Cause**: Database server unavailable or credentials rejected.
- **Diagnostic Steps**:
  1. Inspect backend startup log: `logs/aegivanta.log`.
  2. Check PostgreSQL container status: `docker ps | grep aegivanta_postgres`.
  3. Verify connection string: `DATABASE_URL` in `.env`.

### Symptom 2: Dead Letter Queue (DLQ) Accumulation
- **Root Cause**: Downstream processor error or malformed feature payloads.
- **Diagnostic Steps**:
  1. Inspect metrics: `GET /metrics` -> `aegivanta_stream_dlq_depth`.
  2. Inspect failed event payloads via DLQ inspection API.
  3. Validate feature schema against `ml.schema.feature_schema.FLOW_FEATURE_COLUMNS`.

### Symptom 3: WebSocket Connection Intermittent Drop
- **Root Cause**: Nginx reverse proxy buffering or missing upgrade headers.
- **Resolution**: Verify Ingress annotations in `k8s/ingress.yaml`:
  - `nginx.ingress.kubernetes.io/websocket-services: "sentinelai-api"`
  - `nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"`
  - `nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"`

### Symptom 4: Machine Learning Inference Failure
- **Root Cause**: Preprocessor or model artifact hash mismatch.
- **Resolution**:
  1. Run `python scripts/final_integrity_audit.py`.
  2. Re-verify SHA-256 integrity against `ml/artifacts/artifact_manifest.json`.
