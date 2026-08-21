# PHASE 45 — DEVELOPER PLATFORM API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/developer/summary` | Consolidated Developer Platform Posture Scorecard. |
| `GET` | `/api/v1/developer/keys` | List active scoped API keys for a tenant. |
| `POST` | `/api/v1/developer/keys` | Generate a new scoped developer API key with plaintext secret. |
| `GET` | `/api/v1/developer/webhooks` | List active webhook subscriptions. |
| `POST` | `/api/v1/developer/webhooks` | Create a new webhook subscription and generate HMAC secret. |
| `GET` | `/api/v1/developer/deliveries` | List recent webhook delivery logs and latency. |
| `POST` | `/api/v1/developer/test-dispatch` | Dispatch a signed test event to an external endpoint. |
