# PHASE 32 — CYBER THREAT INTELLIGENCE (CTI) 2.0 ARCHITECTURE

## 1. Executive Summary

Phase 32 delivers an enterprise Cyber Threat Intelligence (CTI) 2.0 platform:
1. **Automated STIX 2.1 & TAXII 2.1 Feed Ingestion**: Ingests structured threat intelligence bundles from CISA AIS, MITRE ATT&CK CTI, AlienVault OTX, and ISACs.
2. **Threat Actor Profiling & Diamond Model Attribution**: In-depth profiles of nation-state and eCrime groups (APT28, APT29, Volt Typhoon, LockBit 3.0, Lazarus Group) mapped across Adversary, Capability, Infrastructure, and Victimology.
3. **Dynamic IOC Confidence Scoring with Sighting Decay**: Exponential time decay ($Score(t) = Score_0 \cdot 2^{-t / T_{1/2}}$) preventing false positives from aged indicators.
4. **MITRE ATT&CK Campaign Technique Heatmaps**: Heat levels (1–5) tracking active adversary TTPs.
5. **Automated Threat Hunting Dispatcher**: Auto-synthesizes KQL and SPL hunting queries directly from newly ingested threat campaigns.

## 2. CTI 2.0 Engine Architecture

```
+-----------------------------------------------------------------------------------+
|                        AEGIVANTA CTI 2.0 & STIX/TAXII ENGINE                      |
|                                                                                   |
|  [TAXII 2.1 Servers: CISA AIS / MITRE CTI / FS-ISAC / AlienVault OTX]             |
|                               |                                                   |
|                               v                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                   STIX 2.1 BUNDLE INGESTION & PARSER                        |  |
|  |  - SDO Parser (Indicator, ThreatActor, Malware, AttackPattern, Campaign)    |  |
|  |  - SRO Linker (Indicates, Uses, Targets, Attributed-To)                     |  |
|  +------------------------------------+----------------------------------------+  |
|                                       |                                           |
|            +--------------------------+--------------------------+                |
|            |                                                     |                |
|            v                                                     v                |
|  +-----------------------------------+     +-----------------------------------+  |
|  |   DIAMOND MODEL ACTOR PROFILES    |     |    DYNAMIC IOC DECAY ENGINE       |  |
|  |  - Adversary & Nation Attribution |     |  - Exponential Time Decay (t1/2)  |  |
|  |  - Capability Implants & TTPs     |     |  - Sighting Counter Boosts        |  |
|  |  - Infrastructure & Fast-Flux     |     |  - Auto-Revocation (>90d stale)   |  |
|  |  - Victimology & Targeted Sectors |     +-----------------+-----------------+  |
|  +-----------------+-----------------+                       |                    |
|                    |                                         |                    |
|                    +--------------------+--------------------+                    |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                     MITRE ATT&CK CAMPAIGN HEATMAPS                          |  |
|  |  - Heat Levels (1-5), Critical TTPs, Active Campaigns                       |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                 AUTOMATED THREAT HUNTING QUERY DISPATCHER                   |  |
|  |  - KQL / SPL / SIEM Hunting Strings Generated & Dispatched to SOC Hunt     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```
