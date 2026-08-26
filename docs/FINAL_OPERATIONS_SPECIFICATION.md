# Aegivanta — Enterprise Operations & Incident Runbook (v25.0.0)

## 1. Routine Operational Procedures
- **Database Backup Verification**: Automated nightly restore test to isolated staging database with checksum validation.
- **Sensor Fleet Token Rotation**: 90-day automated cryptographic token rotation lifecycle.
- **Model Drift & Quality Monitoring**: Continuous tracking of analyst feedback, F1-score, and false-positive rates via `/api/v1/adaptive-ml/drift` and `/api/v1/ai-intelligence/model-drift`.
- **Connector Health & Dead-Letter Auditing**: Review `/api/v1/integrations/health/dashboard` and re-drive DLQ events.
- **FinOps & Capacity Review**: Weekly capacity forecasting and SLO error budget analysis via `/api/v1/global-ops/finops/dashboard`.

## 2. Emergency Incident Procedures
- **Emergency SOAR Kill-Switch**: Disable automated containment immediately via `POST /api/v1/response/kill-switch`.
- **Compromised Sensor Isolation**: Revoke sensor tokens and quarantine host via `POST /api/v1/endpoint-xdr/response/execute` (`action_type: ISOLATE_ENDPOINT`).
- **Endpoint Response Action Rollback**: Reverse automated response actions via `POST /api/v1/endpoint-xdr/response/rollback/{action_id}`.
- **Model Emergency Rollback**: Revert active ML model version to prior stable champion via `POST /api/v1/ai-intelligence/models/{model_id}/rollback`.
