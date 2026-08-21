# Aegivanta — Purple-Team Defensive Attack Simulation Framework (Phase 26.2)

## 10 Safe Attack Simulation Techniques

| Technique Key | Technique Name | MITRE ATT&CK | Tactic | Expected Detection |
|---|---|:---:|---|---|
| `T1110_BRUTE_FORCE` | Simulated Authentication Brute Force | T1110 | Credential Access | `SSH_BRUTE_FORCE_BURST` |
| `T1078_SUSPICIOUS_LOGIN` | Simulated Impossible-Travel Anomaly | T1078 | Defense Evasion | `IMPOSSIBLE_TRAVEL_ANOMALY` |
| `T1068_PRIVILEGE_ESCALATION` | Simulated Local Privilege Escalation | T1068 | Privilege Escalation | `PRIVILEGE_TOKEN_ELEVATION` |
| `T1021_LATERAL_MOVEMENT` | Simulated Multi-Hop SMB Lateral Movement | T1021 | Lateral Movement | `LATERAL_SMB_PROBE` |
| `T1059_MALICIOUS_PROCESS` | Simulated Office Macro Script Execution | T1059 | Execution | `OFFICE_SPAWN_INTERPRETER` |
| `T1059_POWERSHELL` | Simulated Base64 PowerShell Cradle | T1059.001 | Execution | `ENCODED_POWERSHELL_CRADLE` |
| `T1003_CREDENTIAL_DUMPING` | Simulated LSASS Memory Credential Access | T1003 | Credential Access | `CREDENTIAL_DUMPING_MIMIKATZ` |
| `T1547_PERSISTENCE_REGISTRY` | Simulated Run Key Registry Persistence | T1547 | Persistence | `REGISTRY_RUN_KEY_MODIFICATION` |
| `T1486_RANSOMWARE_BEHAVIOR` | Simulated Volume Shadow Copy Deletion | T1486 | Impact | `RANSOMWARE_SHADOW_DELETION` |
| `T1041_DATA_EXFILTRATION` | Simulated Outbound Data Exfiltration | T1041 | Exfiltration | `ANOMALOUS_OUTBOUND_EGRESS` |

## Safety Constraints
- Synthetic telemetry injected through standard pipeline with `is_simulation: true`.
- Zero real-world payload execution or arbitrary shell invocation.
- Deterministic empirical detection latency measurement and coverage calculation.
