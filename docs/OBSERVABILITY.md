# SentinelAI Observability, Health Probes & Telemetry

## 1. Liveness & Readiness Endpoints

- **`GET /health`** (Basic Liveness Probe):
  - Lightweight process liveness check for container orchestrators.
  - Returns `{"status": "HEALTHY", "service": "SentinelAI", "mode": "DEMO", "version": "1.0.0", "environment": "development"}`.
  - Does not fail if background dependencies (database/Redis) are temporarily unreachable.

- **`GET /ready`** (Deep Readiness Probe):
  - Validates full operational readiness before accepting production traffic.
  - Checks: Database connectivity, Redis connection status, active model registry entry, ML model artifact existence (`best_model.joblib`/`preprocessor.joblib`), feature schema compatibility (`validate_artifact_compatibility`).
  - Returns **HTTP 200 OK** when all checks pass.
  - Returns **HTTP 503 Service Unavailable** when any dependency check fails.

---

## 2. Request Correlation & Audit Telemetry

- **Request ID Propagation**: `RequestTimingAndAuditMiddleware` injects or sanitizes correlation IDs via the `X-Request-ID` HTTP header on every incoming and outgoing API request.
- **Audit Logging**: Sensitive system operations (user logins, user creation/deletion, model training, candidate promotion, model rollback, incident state transitions, remediation actions) generate persistent `AuditLog` records containing timestamp, actor ID, role, action, resource, result, operating mode, and request ID. Sensitive data (passwords, JWT tokens, secrets) is strictly excluded.
