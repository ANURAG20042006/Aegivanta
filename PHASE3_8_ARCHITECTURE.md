# SENTINELAI — PHASE 3.8 ARCHITECTURE SPECIFICATION

## Advanced Threat Hunting, Evidence Correlation, Behavioral Investigation & Security Investigation Engine

### 1. Architectural Overview

SentinelAI Phase 3.8 delivers a production-grade **Autonomous Threat Hunting + Security Investigation Engine**. It seamlessly unifies detection telemetry, ML predictions, threat intelligence indicators, attack graphs, and SOAR response workflows into a proactive forensic investigation engine.

```
Telemetry
    ↓
ML Threat Classification (CatBoost/LightGBM/Ensemble)
    ↓
Threat Intelligence (FastIOCCache / Feeds)
    ↓
Detection Correlation Engine (10 Rules / Sliding Windows)
    ↓
Incident Management & Deduplication
    ↓
Attack Graph & Multi-Hop Lateral Movement Detection
    ↓
Deterministic Risk Scoring (0–100 Explainable Breakdown)
    ↓
Autonomous Response & SOAR Policy Engine
    ↓
PHASE 3.8 THREAT HUNTING & INVESTIGATION ENGINE
    ├── Typed Safe Query DSL Engine (No Raw SQL)
    ├── Modular Threat Hunting Rule Pack (HUNT-001 to HUNT-010)
    ├── Investigation Case Management (FSM: OPEN -> TRIAGED -> INVESTIGATING -> ESCALATED -> CONTAINED -> RESOLVED -> CLOSED)
    ├── Evidence Correlation Engine (IP <-> User <-> Host <-> IOC <-> Incident <-> ATT&CK <-> Graph)
    ├── Multi-Dimensional Entity Pivoting Service
    ├── Explainable Behavioral Baseline Engine (Statistical z-score / EWMA)
    ├── Chronological Investigation Timeline Reconstructor
    └── Asynchronous Redis Hunting Stream (`sentinel:hunting`)
```

---

### 2. Core Architectural Components

1. **Threat Hunting Query DSL Engine** ([`backend/app/services/threat_hunting_service.py`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/threat_hunting_service.py)):
   - Whitelist-enforced searchable fields and safe operators (`equals`, `not_equals`, `contains`, `in`, `greater_than`, `less_than`, `between`).
   - Rejects raw SQL injection tokens and bounds page limits.

2. **Modular Threat Hunting Rule Pack** ([`backend/app/hunting/`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/hunting/)):
   - 10 production hunts covering Credential Access, Defense Evasion, Lateral Movement, Exfiltration, Command & Control, Discovery, Impact, Privilege Escalation, and Multi-Stage Attack Chains.

3. **Investigation Case Management Engine** ([`backend/app/services/investigation_case_service.py`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/investigation_case_service.py)):
   - State-machine lifecycle (`OPEN` $\to$ `TRIAGED` $\to$ `INVESTIGATING` $\to$ `ESCALATED` $\to$ `CONTAINED` $\to$ `RESOLVED` $\to$ `CLOSED`).
   - Links incidents, assets, users, IOCs, tags, forensic notes, and evidence items.

4. **Evidence Correlation & Pivoting Engine** ([`backend/app/services/evidence_correlation_service.py`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/evidence_correlation_service.py), [`backend/app/services/investigation_pivot_service.py`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/investigation_pivot_service.py)):
   - Traverses relationship graphs across IPs, accounts, hosts, indicators, and containment actions.

5. **Explainable Behavioral Baseline Engine** ([`backend/app/services/behavior_baseline_service.py`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/behavior_baseline_service.py)):
   - Statistical z-score and rolling baseline deviation calculations without black-box opacity.
