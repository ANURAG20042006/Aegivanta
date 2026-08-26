# PHASE 38 — DETECTION ENGINEERING & COMPLIANCE API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/compliance-detection/summary` | Consolidated Compliance & Detection Engineering Posture Scorecard. |
| `GET` | `/api/v1/compliance-detection/detection-rules` | List candidate and active detection rules. |
| `POST` | `/api/v1/compliance-detection/detection-rules` | Create a candidate detection rule (Sigma / YARA-L). |
| `POST` | `/api/v1/compliance-detection/detection-rules/test-sandbox` | Execute candidate detection rule against test telemetry in safe sandbox. |
| `GET` | `/api/v1/compliance-detection/compliance-controls` | List evaluated compliance controls across regulatory frameworks. |
| `GET` | `/api/v1/compliance-detection/compliance-reports` | List generated compliance audit attestation reports. |
| `POST` | `/api/v1/compliance-detection/compliance-reports/generate` | Generate SHA-256 attested compliance audit report. |
