# Aegivanta — Phase 7: Sensor Fleet Security Architecture

## 1. Authentication & Token Lifecycle
- **Sensor Token Format**: High-entropy 192-bit cryptographic tokens prefixed with `sen_`.
- **Storage**: Plain tokens are never stored in PostgreSQL; only `SHA-256(token)` digests are persisted.
- **Rotation**: 90-day automatic rotation policy. Expired or revoked tokens immediately reject ingestion requests with HTTP 401 Unauthorized.
- **Revocation**: Instant revocation via `DELETE /api/v1/sensors/{id}` or manual admin intervention.

## 2. Ingestion Defense & Hardening
- **Decompression Bomb Protection**: Strict safety threshold rejecting decompressed payloads exceeding 10 MB with HTTP 413.
- **Cross-Tenant Boundary**: Sensor authentication binds every incoming event to the sensor's registered `tenant_id`. Telemetry queries fail closed if tenant context is missing.
- **Replay Protection**: SHA-256 event signature caching discards duplicate events within the 50,000-event sliding window.
