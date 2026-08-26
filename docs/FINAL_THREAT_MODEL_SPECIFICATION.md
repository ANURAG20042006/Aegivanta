# Aegivanta — STRIDE Threat Model & Security Controls (v25.0.0)

## STRIDE Threat Analysis & Implemented Mitigations

| STRIDE Category | Threat Vector | Implemented Mitigation |
|---|---|---|
| **Spoofing** | Forged sensor telemetry injection | Cryptographic rotating enrollment tokens (SHA-256) & mutual auth |
| **Spoofing** | Webhook delivery spoofing | Outbound HMAC-SHA256 signatures with secret keying |
| **Tampering** | Modification of audit records | Immutable append-only audit trail with SHA-256 hash-chain verification |
| **Tampering** | Machine learning model tampering | Cryptographic HMAC-SHA256 model lineage verification and approval gates |
| **Repudiation** | Denied incident response actions | Actor-attributed structured audit logs with IP, user ID, & session linkage |
| **Information Disclosure** | Cross-tenant telemetry leakage | Fail-closed tenant context dependency enforced on every query & table |
| **Information Disclosure** | Credential exposure in integrations | Secrets stored encrypted; omitted from logs and API response payloads |
| **Denial of Service** | Telemetry ingestion flood | Sliding-window rate limiters, 10MB compression-bomb bounds, worker backpressure |
| **Denial of Service** | Webhook replay attacks | Unique UUIDv4 nonces checked in sliding window to block replay attacks |
| **Elevation of Privilege** | Tenant user accessing admin APIs | Strict role-based access control (`TenantRole.ADMIN`) with tenant boundaries |
| **Adversarial AI** | Prompt injection & Model extraction | Prompt sanitizer, output bounded constraints, aggressive rate limits |
