# PHASE 36 — MICROSEGMENTATION & ZTNA API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/microsegmentation/summary` | Consolidated ZTNA & Microsegmentation Posture Scorecard. |
| `GET` | `/api/v1/microsegmentation/connectors` | List active SDP gateway connector nodes. |
| `GET` | `/api/v1/microsegmentation/policies` | List active L4/L7 microsegmentation policies. |
| `POST` | `/api/v1/microsegmentation/policies` | Create and compile a new microsegmentation policy. |
| `GET` | `/api/v1/microsegmentation/sessions` | List active identity-bound ZTNA client access sessions. |
| `POST` | `/api/v1/microsegmentation/sessions/terminate` | Terminate and revoke a client ZTNA session. |
| `GET` | `/api/v1/microsegmentation/lateral-alerts` | List intercepted lateral movement violations. |
| `GET` | `/api/v1/microsegmentation/network-flow-graph` | Get network topology nodes and segment flow links. |
