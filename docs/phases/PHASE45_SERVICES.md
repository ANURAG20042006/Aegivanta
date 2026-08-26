# PHASE 45 — DEVELOPER PLATFORM SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `DeveloperApiKeyService` | `backend/app/services/developer_api_key_service.py` | Generates prefixed API keys (`aeg_live_`), SHA-256 key hashing, and validates granular scopes. |
| `WebhookDispatcherService` | `backend/app/services/webhook_dispatcher_service.py` | Webhook subscription management, HMAC-SHA256 signature generation, live dispatch, and delivery logging. |
| `DeveloperPlatformPostureService` | `backend/app/services/developer_platform_posture_service.py` | Consolidated Developer Platform Scorecard metrics (0–100). |
