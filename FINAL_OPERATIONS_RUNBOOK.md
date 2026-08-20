# Aegivanta — Enterprise Operations & Incident Runbook

## 1. Routine Operational Procedures
- **Database Backup Verification**: Nightly automated restore test to isolated staging database.
- **Sensor Fleet Token Rotation**: 90-day automated token lifecycle trigger.
- **Model Drift Monitoring**: Daily validation of analyst feedback false-positive rates via `/api/v1/adaptive-ml/drift`.

## 2. Emergency Incident Procedures
- **Emergency SOAR Kill-Switch**: Disable automated containment immediately via `POST /api/v1/response/kill-switch`.
- **Compromised Sensor Revocation**: Immediate token blacklisting via `DELETE /api/v1/sensors/{id}`.
