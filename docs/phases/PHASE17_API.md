# Aegivanta — Phase 17: API Specification & Endpoint Directory

## 1. Endpoints Summary

| Method | Endpoint | Description | Scope / RBAC |
|---|---|---|---|
| `GET` | `/api/v1/autonomous-response/policy` | Get active tenant response policy & autonomy level | Tenant Authenticated |
| `PUT` | `/api/v1/autonomous-response/policy` | Update tenant autonomy levels & threshold guards | Tenant Admin |
| `POST` | `/api/v1/autonomous-response/simulate` | Dry-run response simulation & blast-radius calc | Tenant Authenticated |
| `POST` | `/api/v1/autonomous-response/execute` | Execute or queue response action | Analyst / Admin |
| `POST` | `/api/v1/autonomous-response/{id}/rollback` | Rollback reversible response action | Tenant Admin |
| `GET` | `/api/v1/security/validation` | Get latest continuous defense validation results | Tenant Authenticated |
| `POST` | `/api/v1/security/validation/run` | Trigger on-demand defense validation suite | Tenant Admin |
| `POST` | `/api/v1/security/simulations` | Execute purple-team synthetic attack simulation | Tenant Admin |
| `GET` | `/api/v1/security/simulations` | List historical attack simulation runs | Tenant Authenticated |
| `GET` | `/api/v1/security/simulations/{id}` | Get detailed simulation latency & event report | Tenant Authenticated |
| `GET` | `/api/v1/detection/coverage/gaps` | Get ATT&CK detection coverage gaps | Tenant Authenticated |
| `GET` | `/api/v1/security/attack-paths` | Get attack path risk graph & containment cuts | Tenant Authenticated |
| `GET` | `/api/v1/assets/risk` | Get dynamic 0–100 asset risk intelligence | Tenant Authenticated |
| `GET` | `/api/v1/security/control-effectiveness` | Get quantitative defensive control effectiveness | Tenant Authenticated |
