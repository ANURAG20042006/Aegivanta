# SENTINELAI — PHASE 3.8 THREAT HUNTING PACK CATALOG

## Modular Threat Hunting Rules (HUNT-001 through HUNT-010)

| Hunt ID | Name | Severity | MITRE Technique | Tactic | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`HUNT-001`** | Repeated Auth Failure Followed by Success | HIGH | `T1110.001` | Credential Access | Detects failed credential attempts immediately followed by successful session creation. |
| **`HUNT-002`** | New Source IP Privileged Access | CRITICAL | `T1078.004` | Initial Access | Identifies administrative access originating from newly seen foreign/external IPs. |
| **`HUNT-003`** | Unusual Lateral Movement | HIGH | `T1021.002` | Lateral Movement | Detects internal administrative pivots across ports 445 (SMB), 3389 (RDP), or 22 (SSH). |
| **`HUNT-004`** | High-Volume Outbound Exfiltration | HIGH | `T1048` | Exfiltration | Identifies single egress transfers $> 5\text{MB}$ or persistent long connections. |
| **`HUNT-005`** | IOC + Suspicious Authentication Combo | CRITICAL | `T1071.001` | Command & Control | Correlates known Threat Intel indicators with active credential authentications. |
| **`HUNT-006`** | Multi-Asset Account Access | HIGH | `T1087.002` | Discovery | Detects single accounts accessing $> 3$ internal endpoints within short timeframes. |
| **`HUNT-007`** | Rare Destination Port / Unusual Egress | MEDIUM | `T1571` | Command & Control | Detects outbound communication to non-standard C2 egress ports (4444, 1337, etc.). |
| **`HUNT-008`** | High-Velocity Event Burst | HIGH | `T1498` | Impact | Identifies packet velocity floods ($> 1000\text{ pps}$) or volumetric DoS signatures. |
| **`HUNT-009`** | Suspicious Admin Activity / Privilege Escalation | CRITICAL | `T1548` | Privilege Escalation | Detects unauthorized role modifications or token elevation outside normal hours. |
| **`HUNT-010`** | Multi-Stage Attack Sequence | CRITICAL | `T1190` | Execution | Correlates multi-phase progression spanning Recon $\to$ Access $\to$ Lateral $\to$ Exfil. |
