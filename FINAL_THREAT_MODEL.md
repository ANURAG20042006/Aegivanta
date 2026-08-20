# Aegivanta — STRIDE Threat Model & Security Controls

## Threat Analysis & Mitigations

| STRIDE Category | Threat Vector | Implemented Mitigation |
|---|---|---|
| **Spoofing** | Forged sensor telemetry injection | Cryptographic rotating enrollment tokens (SHA-256) |
| **Tampering** | Modification of audit records | Immutable append-only audit trail with hash-chain verification |
| **Repudiation** | Denied incident response actions | Actor-attributed structured audit logs with IP & session linkage |
| **Information Disclosure** | Cross-tenant telemetry leakage | Fail-closed tenant context dependency on all queries |
| **Denial of Service** | Telemetry ingestion flood | Sliding-window rate limiters, compression-bomb 10MB limits |
| **Elevation of Privilege** | Tenant user accessing admin APIs | Role-based access control (`TenantRole.ADMIN`) enforcement |
