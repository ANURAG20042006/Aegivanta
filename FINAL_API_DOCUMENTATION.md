# Aegivanta — Final Master API Reference

## Primary Service Endpoints

| Domain | Method | Endpoint | Purpose |
|---|---|---|---|
| **Auth** | `POST` | `/api/v1/auth/login` | JWT token authentication |
| **Identity** | `POST` | `/api/v1/identity/mfa/setup` | Generate TOTP secret & QR code |
| **SCIM** | `POST` | `/scim/v2/Users` | RFC 7644 user provisioning |
| **Sensors** | `POST` | `/api/v1/sensors/enroll` | Enroll new agent daemon |
| **Sensors** | `POST` | `/api/v1/sensors/ingest` | Gzip compressed telemetry batch ingestion |
| **Detection** | `POST` | `/api/v1/detection-rules` | Deploy versioned Detection-as-Code rule |
| **Copilot** | `POST` | `/api/v1/copilot/query` | Query AI Security Copilot |
| **Compliance**| `GET` | `/api/v1/compliance/posture` | Retrieve SOC 2, ISO 27001, GDPR readiness |
| **Observability**| `GET`| `/metrics` | Prometheus metrics scrape endpoint |
