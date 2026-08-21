# PHASE 31 — ATTACK SURFACE MANAGEMENT (ASM) & CTEM ARCHITECTURE

## 1. Executive Summary

Phase 31 introduces an enterprise Continuous Threat Exposure Management (CTEM) and Attack Surface Management (ASM) engine:
1. **External Perimeter Reconnaissance**: Continuous asset discovery across FQDNs, subdomains, cloud endpoints, IP ranges, and BGP ASNs.
2. **Dangling DNS & Subdomain Takeover Guard**: Scans DNS CNAME records for orphaned cloud services (AWS S3, GitHub Pages, Azure App Services) preventing unauthorized subdomain claim.
3. **Dark Web Credential Breach Intelligence**: Correlates corporate domain emails against underground infostealer dumps, pastebins, and darknet marketplaces.
4. **Brand Protection & Typosquatting Monitor**: Levenshtein similarity analysis identifying fraudulent lookalike domains and phishing lures with active MX records.
5. **Gartner 5-Stage CTEM Prioritization**: Scoping -> Discovery -> Prioritization -> Validation -> Mobilization combining EPSS, CVSS v3.1, and CISA KEV.

## 2. CTEM & Attack Surface Recon Flow

```
+-----------------------------------------------------------------------------------+
|               AEGIVANTA ATTACK SURFACE MANAGEMENT & CTEM ARCHITECTURE             |
|                                                                                   |
|  [External Perimeter: Domains, Subdomains, IPs, Cloud Buckets, ASNs]              |
|                             |                                                     |
|                             v                                                     |
|  +-----------------------------------------------------------------------------+  |
|  |                 DISCOVERY & RECONNAISSANCE ENGINE                           |  |
|  |  - Port Scanning (RDP 3389, SSH 22, K8s 6443, Redis 6379, Elasticsearch)   |  |
|  |  - SSL/TLS Health (Expiration countdown, weak cipher detection)             |  |
|  |  - Dangling DNS Takeover Checks (Unclaimed S3 / GitHub Pages pointers)      |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                 THREAT INTELLIGENCE & BRAND PROTECTION                      |  |
|  |  - Dark Web Credential Breach Ingestion (Infostealer logs, pastebin leaks)  |  |
|  |  - Typosquatting / Lookalike Detection (Levenshtein similarity, active MX)  |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                 GARTNER 5-STAGE CTEM PRIORITIZATION MATRIX                  |  |
|  |  1. Scoping -> 2. Discovery -> 3. Prioritization (EPSS + CVSS + CISA KEV)  |  |
|  |  4. Validation -> 5. Mobilization (Automated SOAR Playbooks & Jira Tickets) |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```
