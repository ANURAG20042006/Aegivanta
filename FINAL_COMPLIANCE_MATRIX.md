# Aegivanta — Regulatory Compliance & Framework Matrix

| Framework | Control Code | Description | Implementation Status |
|---|---|---|---|
| **SOC 2 Type II** | CC6.1 | Logical Access Controls & MFA | 🟢 Implemented (TOTP MFA / SSO) |
| **SOC 2 Type II** | CC6.6 | Boundary Protection & Network Filtering | 🟢 Implemented (IP Allowlist / Firewall) |
| **SOC 2 Type II** | CC7.2 | Security Anomaly Detection | 🟢 Implemented (CatBoost ML / Detection-as-Code) |
| **ISO 27001:2022** | A.5.15 | Access Control Management | 🟢 Implemented (RBAC / SCIM 2.0) |
| **ISO 27001:2022** | A.8.16 | Monitoring Activities & Audit Logs | 🟢 Implemented (Immutable Audit Trail) |
| **GDPR** | Art. 32 | Security of Data Processing | 🟢 Implemented (TLS 1.3 / Tenant Isolation) |
| **NIST CSF 2.0** | DE.AE | Anomalies & Real-Time Event Detection | 🟢 Implemented (Real-Time Ingestion Pipeline) |
| **NIST CSF 2.0** | RS.RP | Response Execution & Containment | 🟢 Implemented (SOAR Playbooks & Approvals) |
