# Aegivanta — Phase 17: Continuous Security Validation Specification

## 1. Automated Defense Auditing
The continuous defense validation engine runs automated, non-destructive audit checks:
- **Identity**: Mandatory MFA policy enforcement.
- **Tenant Isolation**: Foreign-key cascade partitioning and query scoping.
- **Sensor Security**: Token freshness and real-time heartbeat ingestion.
- **Detection Rules**: AST rule safety and MITRE ATT&CK taxonomy alignment.
- **Audit Integrity**: Cryptographic HMAC-SHA256 audit log hash-chain verification.

## 2. API Endpoints
- `GET /api/v1/security/validation`
- `POST /api/v1/security/validation/run`
