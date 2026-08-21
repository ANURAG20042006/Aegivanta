# PHASE 32 — AUTOMATED THREAT HUNTING QUERY DISPATCH SPECIFICATION

## 1. Automated Query Synthesis

From threat actor TTP mappings, Aegivanta synthesizes multi-dialect hunting queries:
- **KQL (Microsoft Sentinel / Defender)**: Process execution anomalies and PowerShell encoded scripts.
- **SPL (Splunk)**: Network flow, VPN gateway session analysis, and firewall deny surges.
- **SIEM Rules**: Automated correlation rule creation.
