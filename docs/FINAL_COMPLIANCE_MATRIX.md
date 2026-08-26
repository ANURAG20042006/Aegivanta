# Aegivanta — Regulatory Compliance & Framework Matrix (v25.0.0)

| Framework | Control Code | Description | Implementation Status |
|---|---|---|---|
| **SOC 2 Type II** | CC6.1 | Logical Access Controls & MFA | 🟢 Implemented (TOTP MFA / SSO / SCIM) |
| **SOC 2 Type II** | CC6.6 | Boundary Protection & Network Filtering | 🟢 Implemented (IP Allowlist / Zero-Trust) |
| **SOC 2 Type II** | CC6.8 | Unauthorized System & Software Detection | 🟢 Implemented (EDR / Cloud Security) |
| **SOC 2 Type II** | CC7.2 | Security Anomaly Detection | 🟢 Implemented (Multi-Model ML / Detection-as-Code) |
| **ISO 27001:2022** | A.5.15 | Access Control Management | 🟢 Implemented (RBAC / SCIM 2.0 / IAM Analyzer) |
| **ISO 27001:2022** | A.8.16 | Monitoring Activities & Audit Logs | 🟢 Implemented (Immutable Audit Hash-Chain) |
| **ISO 27001:2022** | A.8.28 | Secure Coding & Software Architecture | 🟢 Implemented (HMAC Webhooks / Strict Typing) |
| **GDPR** | Art. 32 | Security of Data Processing | 🟢 Implemented (TLS 1.3 / Tenant Isolation / AES) |
| **NIST CSF 2.0** | GV.OC | Governance & Oversight | 🟢 Implemented (Model Governance / Compliance Posture) |
| **NIST CSF 2.0** | DE.AE | Anomalies & Real-Time Event Detection | 🟢 Implemented (Real-Time Ingestion / EDR / XDR) |
| **NIST CSF 2.0** | RS.RP | Response Execution & Containment | 🟢 Implemented (SOAR 2.0 Playbooks & Approval Gates) |
| **CIS Controls v8** | Control 10 | Malware Defenses | 🟢 Implemented (EDR Behavioral Detection Rules) |
| **CIS Controls v8** | Control 13 | Network Monitoring and Defense | 🟢 Implemented (Packet / Flow Analysis & TIP) |
