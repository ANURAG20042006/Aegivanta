# AEGIVANTA — THREAT MODEL & MITRE ATT&CK MATRIX

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  

---

## 1. Threat Landscape & Ingestion Attack Vectors

Aegivanta monitors and neutralizes threats across the entire cyber kill chain:

| MITRE ATT&CK Tactic | Technique ID & Name | Detection Mechanism | Automated SOAR Playbook |
|---|---|---|---|
| **Reconnaissance** | T1595 Active Scanning (Port Scan) | Flow packets/sec + SYN flag ratio + ML Classifier | `RATE_LIMIT_IP` + Alert SOC |
| **Initial Access** | T1190 Exploit Public-Facing App (SQLi/XSS) | Payload pattern recognition & abnormal payload length | `BLOCK_IP` (Immediate WAF containment) |
| **Execution** | T1059 Command & Scripting Interpreter | Anomaly detection in egress packet volume | `ISOLATE_HOST` |
| **Persistence** | T1136 Create Account | RBAC user creation audit monitor | `DISABLE_ACCOUNT` + Revoke Tokens |
| **Lateral Movement** | T1021 Remote Services (SMB / SSH / RDP) | Multi-hop attack graph traversal & 300s windowing | `QUARANTINE_ASSET` + Session termination |
| **Exfiltration** | T1048 Exfiltration Over Alternative Protocol | Egress flow duration & large outbound packet volume | `BLOCK_IP` + Port Isolation |
| **Impact** | T1498 Network Denial of Service (DDoS) | Volumetric flow rate spike & CatBoost prediction | `BLOCK_IP` (Upstream sinkhole / ACL) |

---

## 2. Platform Attack Surface Hardening (STRIDE Analysis)

| Threat Category | Potential Attack Vector | Aegivanta Platform Safeguard |
|---|---|---|
| **Spoofing** | Forged JWT identity tokens | Cryptographic signature verification using HMAC-SHA256 with minimum 32-byte secret. |
| **Tampering** | Modification of ML model files | SHA-256 manifest hash verification on every application startup. |
| **Repudiation** | Denying execution of containment actions | Immutable database audit ledger recording actor, timestamp, IP, and outcome. |
| **Information Disclosure** | Token or password leakage in logs | Context log sanitizer redacting sensitive keys before emitting JSON. |
| **Denial of Service** | Telemetry ingestion queue flooding | In-memory + distributed Redis rate limiters and atomic SHA-256 deduplication. |
| **Elevation of Privilege** | Normal user escalating to SOC Admin | Enforced RBAC dependency filters (`require_role(["admin"])`) on all mutations. |
