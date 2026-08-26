# Aegivanta — Phase 13: Governance, Audit & Compliance Architecture

## 1. Tamper-Evident HMAC Audit Chaining
Every critical system action writes an append-only audit record:
- Records are hashed via SHA-256 HMAC using `SECRET_KEY`.
- Each record links to the previous record's hash (`prev_hash`), forming a verifiable cryptographic hash chain.
- Tamper detection is performed via `ImmutableAuditService.verify_chain_integrity()`.

## 2. Regulatory Compliance Posture Engine
Exposed at `GET /api/v1/compliance/posture`:
- **SOC 2 Type II**: CC6.1 (Access Controls), CC6.6 (Firewall / Network), CC7.2 (Anomaly Detection), CC7.4 (Incident Remediation).
- **ISO/IEC 27001:2022**: A.5.15 (Access Control), A.8.16 (Monitoring & Logging), A.8.20 (Network Security).
- **GDPR**: Art. 32 (Data Security), Art. 33 (72h Breach Notification).
- **NIST CSF 2.0**: ID.AM (Asset Inventory), DE.AE (Anomalies Detection), RS.RP (Response Execution).
