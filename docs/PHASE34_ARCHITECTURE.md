# PHASE 34 — ADAPTIVE RISK-BASED VULNERABILITY MANAGEMENT (RBVM) & EPSS 2.0 ARCHITECTURE

## 1. Executive Summary

Phase 34 delivers an enterprise Adaptive Risk-Based Vulnerability Management (RBVM) platform:
1. **Multi-Factor RBVM Risk Scoring Matrix**: Combines CVSS v3.1 base score, EPSS 2.0 exploit probability, CISA Known Exploited Vulnerabilities (KEV) flag, ransomware campaign links, and asset criticality weighting.
2. **EPSS 2.0 Exploit Probability Engine**: Empirical likelihood calculation (0.00% to 100.00%) and percentile mapping.
3. **Automated Remediation SLA Timers**: Classifies CVE exposures into actionable SLA windows (24h for P0, 72h for P1, 14d for P2, 30d for P3).
4. **WAF & IPS Virtual Patching Compensating Controls**: Automated generation and deployment of AWS WAF regexes, ModSecurity rules, and Suricata IPS signatures.
5. **Remediation Campaign Orchestrator**: Aggregates CVEs across infrastructure fleets and tracks burn-down progress.

## 2. RBVM System Architecture

```
+-----------------------------------------------------------------------------------+
|               AEGIVANTA ADAPTIVE RBVM & EPSS 2.0 VULNERABILITY ENGINE             |
|                                                                                   |
|  [Vulnerability Feeds: NVD / EPSS 2.0 / CISA KEV / Threat Intel Campaigns]        |
|                               |                                                   |
|                               v                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                 COMPOSITE RBVM RISK SCORING ALGORITHM                       |  |
|  |  Risk = (CVSS*3.5) + (EPSS*35.0) + (KEV*20.0) + (Ransomware*10.0) * Tier    |  |
|  +------------------------------------+----------------------------------------+  |
|                                       |                                           |
|            +--------------------------+--------------------------+                |
|            |                                                     |                |
|            v                                                     v                |
|  +-----------------------------------+     +-----------------------------------+  |
|  |   PRIORITIZED REMEDIATION SLAS    |     |  WAF/IPS VIRTUAL PATCHING ENGINE  |  |
|  |  - P0 Critical: 24h SLA           |     |  - AWS WAF JSON Rules             |  |
|  |  - P1 High: 72h SLA               |     |  - ModSecurity / Coraza CRS Rules |  |
|  |  - P2 Medium: 14-day SLA          |     |  - Suricata / Snort Signatures    |  |
|  |  - P3 Low: 30-day SLA             |     |  - Runtime Zero-Day Mitigation    |  |
|  +-----------------+-----------------+     +-----------------+-----------------+  |
|                    |                                         |                    |
|                    +--------------------+--------------------+                    |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                REMEDIATION CAMPAIGNS & BURN-DOWN TRACKER                    |  |
|  |  - Asset Target Counts, Completed Fixes, Owner Teams, Due Dates             |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```
