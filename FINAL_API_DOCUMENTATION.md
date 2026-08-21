# Aegivanta — Final Master API Reference (v25.0.0)

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
| **Threat Intel** | `GET` | `/api/v1/threat-intel/platform/summary` | Retrieve threat intelligence summary |
| **SOAR 2.0** | `POST` | `/api/v1/soar/playbooks/execute` | Execute declarative SOAR playbook |
| **AI Intelligence**| `GET` | `/api/v1/ai-intelligence/models` | List governed ML detection models |
| **Cloud Security** | `GET` | `/api/v1/cloud-security/inventory` | List multi-cloud asset inventory |
| **Endpoint XDR** | `POST` | `/api/v1/endpoint-xdr/telemetry` | Ingest EDR process/file/registry telemetry |
| **Zero-Trust** | `GET` | `/api/v1/endpoint-xdr/posture/devices` | Query Zero-Trust device trust scores |
| **Integrations** | `GET` | `/api/v1/integrations/marketplace/catalog` | List 17+ security ecosystem connectors |
| **Global Ops** | `GET` | `/api/v1/global-ops/finops/dashboard` | Retrieve FinOps cost analytics and SRE SLOs |
| **Compliance** | `GET` | `/api/v1/compliance/posture` | Retrieve SOC 2, ISO 27001, GDPR readiness |
| **Observability** | `GET` | `/metrics` | Prometheus metrics scrape endpoint |
