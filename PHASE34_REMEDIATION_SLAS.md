# PHASE 34 — REMEDIATION SLA WINDOWS SPECIFICATION

## 1. Prioritization & SLA Windows

| Priority Tier | Trigger Criteria | Remediation SLA |
|:---|:---|:---:|
| **P0_CRITICAL** | EPSS $\ge 0.70$ OR CISA KEV on Tier 1 Asset OR RBVM $\ge 85.0$ | **24 Hours** |
| **P1_HIGH** | CVSS $\ge 8.0$ AND EPSS $\ge 0.30$ OR RBVM $\ge 65.0$ | **72 Hours** |
| **P2_MEDIUM** | CVSS $\ge 6.0$ OR RBVM $\ge 40.0$ | **14 Days** |
| **P3_LOW** | CVSS $< 6.0$ AND EPSS $< 0.10$ | **30 Days** |
