# SentinelAI Phase 4 — SaaS API Specification Matrix

## 1. Multi-Tenant SaaS Endpoints

| Method | Endpoint | Auth Required | Minimum Role / Scope | Purpose |
|---|---|---|---|---|
| `POST` | `/api/v1/organizations` | JWT | User | Create customer organization & default workspace |
| `GET` | `/api/v1/organizations/me` | JWT | User | List organizations current user belongs to |
| `GET` | `/api/v1/organizations/{id}/members` | JWT | `SECURITY_ANALYST` | List member directory and assigned roles |
| `POST` | `/api/v1/organizations/{id}/members` | JWT | `ADMIN` | Invite or add a member to the organization |
| `POST` | `/api/v1/tenants` | JWT | `ADMIN` | Create an isolated workspace tenant |
| `GET` | `/api/v1/tenants` | JWT | User | List all workspace tenants in active organization |
| `GET` | `/api/v1/tenants/{id}/settings` | JWT | User | Retrieve compliance, MFA, and retention settings |
| `PUT` | `/api/v1/tenants/{id}/settings` | JWT | `ADMIN` | Update compliance, MFA, and retention settings |
| `POST` | `/api/v1/api-keys` | JWT / Key | `API_ADMIN` / `ADMIN` | Generate customer API key (one-time secret display) |
| `GET` | `/api/v1/api-keys` | JWT / Key | `API_ADMIN` / `ADMIN` | List active/revoked API keys (masked secrets) |
| `DELETE` | `/api/v1/api-keys/{id}` | JWT / Key | `API_ADMIN` / `ADMIN` | Revoke API key |
| `GET` | `/api/v1/subscriptions/current` | JWT | User | Fetch active plan tier and feature entitlements |
| `GET` | `/api/v1/subscriptions/usage` | JWT | User | Fetch monthly metered telemetry vs plan quotas |
| `POST` | `/api/v1/subscriptions/upgrade` | JWT | `BILLING_ADMIN` | Upgrade commercial plan tier |
| `POST` | `/api/v1/subscriptions/checkout-session` | JWT | `BILLING_ADMIN` | Generate billing checkout URL |
| `POST` | `/api/v1/billing/webhook` | Webhook Sig | HMAC-SHA256 | Ingest and idempotently process billing webhooks |
| `GET` | `/api/v1/onboarding/status` | JWT | User | Calculate guided onboarding setup progress |
| `POST` | `/api/v1/sensors/enroll` | JWT | `ADMIN` | Enroll endpoint/network sensor agent |
| `POST` | `/api/v1/sensors/{id}/heartbeat` | Sensor Token | Agent | Ingest agent heartbeat and telemetry stats |
| `GET` | `/api/v1/sensors` | JWT | User | List enrolled sensors and health status |
| `DELETE` | `/api/v1/sensors/{id}` | JWT | `ADMIN` | Revoke sensor agent enrollment |
| `POST` | `/api/v1/integrations` | JWT | `ADMIN` | Register external SIEM/Slack/EDR connector |
| `GET` | `/api/v1/integrations` | JWT | User | List configured integration connectors |
| `POST` | `/api/v1/integrations/{id}/test` | JWT | `ADMIN` | Trigger test notification dispatch |
| `DELETE` | `/api/v1/integrations/{id}` | JWT | `ADMIN` | Delete integration connector |
