# SentinelAI Phase 4 — Customer Onboarding Workflow

## 1. Guided Setup Lifecycle

```
[1. User Registration / Login]
         ↓
[2. Organization & Workspace Creation]
         ↓
[3. Subscription Tier & Entitlement Selection]
         ↓
[4. Telemetry Sensor Enrollment & API Key Setup]
         ↓
[5. Live Ingestion Verification & SOC Dashboard Access]
```

---

## 2. Onboarding Status API

- Endpoint: `GET /api/v1/onboarding/status`
- Response Payload:
  ```json
  {
    "has_organization": true,
    "organization_name": "Acme Defense Systems",
    "organization_slug": "acme-defense",
    "has_tenant": true,
    "tenant_name": "Acme Defense Systems (Production)",
    "has_sensor": true,
    "sensor_count": 2,
    "has_telemetry": true,
    "current_step": 4,
    "completed": true
  }
  ```
