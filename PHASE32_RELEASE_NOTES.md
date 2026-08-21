# PHASE 32 — RELEASE NOTES (v32.0.0)

## 1. Release Highlights

- **Automated STIX 2.1 & TAXII 2.1 Engine**: Ingests threat feeds from CISA AIS, MITRE ATT&CK CTI, AlienVault OTX, and FS-ISAC with on-demand polling.
- **Threat Actor Profiling & Diamond Model**: In-depth profiles of APT28, APT29, Volt Typhoon, LockBit 3.0, and Lazarus Group.
- **Dynamic IOC Confidence Scoring with Sighting Decay**: Exponential time decay algorithm reducing false alarms on aged threat observables.
- **MITRE ATT&CK Campaign Technique Heatmaps**: Heat scoring (1–5) for weaponized threat campaigns.
- **Automated Threat Hunting Dispatcher**: Instant synthesis of KQL and SPL hunting strings.
- **6-Tab Frontend Command Center**: Interactive `ThreatIntelCenterV2.tsx` with Diamond Model cards and hunting query generator.
- **Zero-Failure Verification**: 100% test pass rate across 10 test suites and clean Vite production build.
