# PHASE 40 — FEDERATED THREAT SHARING API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/federated-threat/summary` | Consolidated Federated Threat Sharing Posture Scorecard. |
| `GET` | `/api/v1/federated-threat/nodes` | List verified peer exchange nodes across the federation. |
| `GET` | `/api/v1/federated-threat/indicators` | List anonymized federated threat indicators with consensus confidence. |
| `POST` | `/api/v1/federated-threat/indicators/share` | Anonymize and share newly discovered indicator to federated mesh. |
| `POST` | `/api/v1/federated-threat/blind-match` | Execute zero-knowledge homomorphic encrypted blind match query. |
