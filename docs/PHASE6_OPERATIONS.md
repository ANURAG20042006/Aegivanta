# Aegivanta Phase 6 — Sensor Fleet Operations Runbook

## 1. Fleet Monitoring & Alarms

- **Degraded Agent Alarm**: Triggered when `health_score < 70` (indicating event drops or local buffer saturation).
- **Offline Agent Alarm**: Triggered when `last_heartbeat > 300s` (5 minutes).
- **Token Rotation Cadence**: Recommended 90-day cycle using `POST /api/v1/sensors/{id}/rotate-token`.

## 2. Emergency Agent Revocation
When a host is suspected of being compromised:
```http
DELETE /api/v1/sensors/{sensor_id}
Authorization: Bearer <ADMIN_JWT>
```
The ingestion gateway will immediately reject all subsequent ingestion requests from that sensor token with HTTP 401.
