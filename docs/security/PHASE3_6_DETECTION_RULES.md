# SentinelAI — Phase 3.6 Detection Rules Catalog

## Production Detection Rules (RULE-001 through RULE-010)

| Rule ID | Rule Name | Severity | MITRE ATT&CK Techniques | Detection Logic & Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **RULE-001** | Repeated Authentication Failures | HIGH | `T1110.001`, `T1110.003` | Detects brute-force authentication bursts ($\ge 5$ failures within sliding window). |
| **RULE-002** | Impossible Authentication Pattern | CRITICAL | `T1078.004`, `T1078` | Detects concurrent logins across impossible geographic transit speeds ($> 1000\text{ km/h}$). |
| **RULE-003** | IOC Matched Against Telemetry | HIGH / CRITICAL | `T1071.001`, `T1566` | Matches flow source/dest IP or domain against active Threat Intelligence IOC cache. |
| **RULE-004** | Suspicious Lateral Movement Sequence | HIGH / CRITICAL | `T1021.002`, `T1021.001`, `T1021.004` | Detects internal administrative pivots across SMB (445), RDP (3389), SSH (22), WinRM (5985). |
| **RULE-005** | High-Risk Multi-Hop Attack Path | CRITICAL | `T1021`, `T1570` | Identifies multi-hop internal attack trajectories spanning $\ge 3$ consecutive hops. |
| **RULE-006** | Crown-Jewel Asset Exposure | CRITICAL | `T1087`, `T1078.001` | Identifies attack blast radius reaching Tier-1 protected crown jewel databases/assets. |
| **RULE-007** | Abnormal Outbound Connection Pattern | HIGH | `T1048`, `T1041` | Detects abnormal long-duration ($> 3600\text{s}$) or high-volume ($> 10\text{MB}$) egress flows. |
| **RULE-008** | Potential Credential Abuse | CRITICAL | `T1558`, `T1078` | Detects Kerberos pass-the-ticket, token manipulation, or port 88 credential exploitation. |
| **RULE-009** | Repeated Security Policy Violation | MEDIUM | `T1046`, `T1595.001` | Identifies systematic reconnaissance port scans or unauthorized subnet probing. |
| **RULE-010** | High-Velocity Suspicious Event Burst | HIGH / CRITICAL | `T1498`, `T1499` | Detects high packet velocity floods ($> 1000\text{ packets/sec}$) or Denial of Service patterns. |

---

### In-Memory Evaluation Performance

- **Evaluated Rules**: 10
- **Average Latency**: `0.0171 ms` per event (Requirement: $< 5.0\text{ ms}$)
- **Deterministic**: 100% test-verified, zero non-deterministic random scoring
