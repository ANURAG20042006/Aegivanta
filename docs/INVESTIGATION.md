# SentinelAI Automated Investigations & MITRE ATT&CK Mapping

## Overview
SentinelAI Automated Investigation Service aggregates multi-signal security evidence across alerts, flow telemetry, threat intelligence IOCs, and behavioral anomalies to reconstruct attack chains and suggest actionable analyst responses.

## MITRE ATT&CK Matrix Stage Mapping
The system deterministically maps detected attack patterns to MITRE ATT&CK tactics:

| Attack Signature | MITRE ATT&CK Stage |
|---|---|
| `PortScan`, `Bot` | `RECONNAISSANCE` |
| `FTP-Patator`, `SSH-Patator`, `Web Attack – Brute Force` | `INITIAL_ACCESS` |
| `Web Attack – XSS`, `Web Attack – Sql Injection` | `EXECUTION` |
| `Infiltration` | `LATERAL_MOVEMENT` |
| `Heartbleed` | `EXFILTRATION` |
| `DoS/DDoS`, `DoS Hulk`, `DoS GoldenEye`, `DoS slowloris`, `DoS Slowhttptest`, `DoS_Service_Outage` | `IMPACT` |

## Evidence Graph Structure
- **Correlated Alerts**: Chronologically ordered alert objects with risk scores and feature importances.
- **IOC Hits**: Threat intelligence attribution, feed source, confidence score, and hit frequency.
- **Behavioral Anomalies**: Asset baseline deviation metrics ($z \ge 3.0$) and English rationale.
- **Recommendations**: RBAC-safe deterministic next actions for Tier-1 and Tier-2 SOC analysts.
