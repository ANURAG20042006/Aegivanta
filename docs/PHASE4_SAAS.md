# SentinelAI Phase 4 — SaaS Commercialization Architecture

## 1. Product Capabilities

SentinelAI v4.0 offers four commercial editions:
- **Free / Community Edition**: Basic deterministic detection rules, SOC dashboard, 3 user seats, 5GB monthly telemetry.
- **Professional Edition**: Threat Intelligence IOC feeds, Attack Graph analytics, Investigation workbenches, 10 user seats, 50GB telemetry.
- **Business Edition**: Autonomous SOAR containment, Threat Hunting workbench, customer API keys, SIEM & Slack connectors, 25 user seats, 250GB telemetry.
- **Enterprise Edition**: Adaptive ML detection ensemble, dedicated worker autoscaling, custom 365-day retention, unlimited seats, 5TB monthly telemetry, Enterprise SSO.

---

## 2. Technical Safeguards

- **Zero Data Leakage**: Authenticated tenant boundary enforced in `TenantContext` at API and database query levels.
- **Fail Closed**: Missing or invalid tenant roles result in immediate HTTP 403 `PermissionDeniedError`.
- **Zero Secrets in Storage**: API keys and sensor enrollment tokens are hashed with SHA-256 before database insertion.
- **Deterministic Billing**: Incoming webhooks must pass HMAC-SHA256 signature verification and idempotency deduplication.
