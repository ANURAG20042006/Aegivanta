# PHASE E — API SECURITY MATRIX & ATTACK SURFACE INVENTORY

**Document Date**: August 26, 2026  
**Auditor**: Senior API Security Architect  
**Target Repository**: Aegivanta / SentinelAI  

---

## API Endpoint Security Catalog

| HTTP Method | Path Pattern | Authentication Required | Authorization / RBAC | Tenant Scoped | Input Validation Schema | Rate Limit Applied | Security Test Reference |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `POST` | `/api/v1/auth/login` | No | Public | N/A | `OAuth2PasswordRequestForm` | 10 req / min | `test_auth_login_bruteforce` |
| `POST` | `/api/v1/auth/register` | No | Public | N/A | `UserCreate` Pydantic model | 5 req / min | `test_auth_registration` |
| `GET` | `/api/v1/assets/` | Yes (Bearer JWT) | `require_tenant_role(VIEWER)` | Yes (`ctx.tenant_id`) | Query parameters | 100 req / min | `test_assets_tenant_isolation` |
| `POST` | `/api/v1/assets/` | Yes (Bearer JWT) | `require_tenant_role(ADMIN)` | Yes (`ctx.tenant_id`) | `AssetCreate` Pydantic model | 50 req / min | `test_assets_create_idor` |
| `GET` | `/api/v1/alerts/` | Yes (Bearer JWT) | `require_tenant_role(VIEWER)` | Yes (`ctx.tenant_id`) | Filter parameters | 100 req / min | `test_alerts_scoped_query` |
| `GET` | `/api/v1/incidents/` | Yes (Bearer JWT) | `require_tenant_role(VIEWER)` | Yes (`ctx.tenant_id`) | Pagination & filters | 100 req / min | `test_incidents_tenant_scoping` |
| `POST` | `/api/v1/predict/` | Yes (Bearer JWT) | `require_role(["analyst", "admin"])`| Yes | `PacketFeatureVector` (30 features) | 200 req / min | `test_predict_schema_validation` |
| `POST` | `/api/v1/pcap/upload`| Yes (Bearer JWT) | `require_role(["analyst", "admin"])`| Yes | Binary PCAP stream (max 50MB) | 20 req / min | `test_pcap_binary_fuzzing` |
| `GET` | `/api/v1/sensors/` | Yes (Bearer JWT) | `require_tenant_role(VIEWER)` | Yes (`ctx.tenant_id`) | Query parameters | 100 req / min | `test_sensors_fleet_isolation` |
| `POST` | `/api/v1/sensors/{id}/token`| Yes (Bearer JWT)| `require_tenant_role(ADMIN)`| Yes (`ctx.tenant_id`) | Path ID | 30 req / min | `test_sensors_token_rotation_idor` |
| `POST` | `/api/v1/response/approve` | Yes (Bearer JWT) | `require_tenant_role(ADMIN)` | Yes (`ctx.tenant_id`) | `ApprovalRequest` model | 30 req / min | `test_soar_approval_rbac` |
| `GET` | `/api/v1/audit/logs` | Yes (Bearer JWT) | `require_tenant_role(OWNER)` | Yes (`ctx.tenant_id`) | Range & actor filters | 50 req / min | `test_audit_tamper_evidence` |
| `GET` | `/api/v1/ws/telemetry` | Yes (Query JWT) | Normalized Active DB User | Yes (`ConnectionManager`) | WebSocket frame | 50 max connections | `test_websocket_tenant_bleeding` |

---
