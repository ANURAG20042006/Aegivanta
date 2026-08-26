# PHASE 32 — FRONTEND THREAT INTEL 2.0 COMMAND CENTER

## 1. UI Tabs

`ThreatIntelCenterV2.tsx` delivers a 6-tab enterprise interface:
1. **CTI 2.0 Overview**: CTI Posture score, active TAXII feeds, active indicators, top nation-state/eCrime actors, and priority hunting recommendations.
2. **Threat Actor Profiles**: Diamond Model attribution cards (Adversary, Capability, Infrastructure, Victimology), targeted industries, and MITRE TTPs.
3. **STIX/TAXII Feeds**: Automated feed manager with reputation scores, poll interval controls, and on-demand **Poll Now** triggers.
4. **IOC Ledger & Decay**: Dynamic indicator table with initial score, current decayed confidence score, and sighting counts.
5. **Campaign Heatmaps**: MITRE ATT&CK technique heat cards (Heat levels 1–5).
6. **Hunting Dispatcher**: Auto-synthesizes KQL/SPL hunting queries with single-click clipboard copying.
