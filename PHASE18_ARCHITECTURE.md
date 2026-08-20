# AEGIVANTA — PHASE 18 PLATFORM ARCHITECTURE

## Enterprise Threat Intelligence & Threat Hunting Platform

### 1. System Overview
Aegivanta Phase 18 upgrades the platform's threat intelligence and hunting architecture into an enterprise-grade adversary profiling, feed federation, transparent scoring, and analyst hunting workbench.

```mermaid
graph TD
    A[External Feeds: STIX/TAXII / MISP / OTX / Abuse.ch] -->|SSRF Guard & Deduplication| B[Threat Intelligence Feed Engine]
    B --> C[Normalized Threat Indicators]
    C --> D[Threat Scoring Engine 0-100 & Decay]
    E[Adversary Profiles: Threat Actors / Campaigns] --> D
    F[Customer Network Sensors] -->|Sightings Tracking| D
    D --> G[Unified Intelligence Correlation Engine]
    G --> H[Threat Hunting Workbench]
    G --> I[Threat Graph Topology]
    H --> J[Analyst SOC Console]
```

### 2. Core Architecture Modules
- **Threat Actor & Campaign Profiler**: Multi-stage adversary attribution (Nation-State, Cybercriminal, Hacktivist) with MITRE technique alignment.
- **Federated Feed Ingestion**: Extensible provider architecture with SSRF validation preventing internal IP querying.
- **Transparent Threat Scoring (0–100)**: Multi-factor scoring incorporating source reliability, confidence, sightings frequency, severity, and time decay.
- **Analyst Threat Hunting Workbench**: Query builder and reusable hunting templates across IPs, domains, hashes, lateral movement, and ATT&CK techniques.
