# PHASE 43 — DATA GOVERNANCE & DSAR API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/governance-dsar/summary` | Consolidated Data Governance & DSAR Scorecard. |
| `GET` | `/api/v1/governance-dsar/lineage` | List telemetry provenance and lineage pipeline stages. |
| `GET` | `/api/v1/governance-dsar/legal-holds` | List active and historical legal hold orders. |
| `POST` | `/api/v1/governance-dsar/legal-holds` | Issue new forensic legal hold order. |
| `GET` | `/api/v1/governance-dsar/requests` | List GDPR / CCPA DSAR privacy requests. |
| `POST` | `/api/v1/governance-dsar/requests` | Submit and execute a new DSAR privacy request. |
