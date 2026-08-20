# SENTINELAI — PHASE 3.8 IMPLEMENTATION PLAN

## Advanced Threat Hunting, Evidence Correlation, Behavioral Investigation & Security Investigation Engine

### 1. Architectural Scope & Integration Map

Phase 3.8 integrates naturally with the existing SentinelAI pipeline:

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

### 2. Sub-Phase Breakdown

- **3.8.1: Database Models & Entity Relations**:
  - `InvestigationCase`, `InvestigationEvidence`, `InvestigationNote`, `InvestigationTimeline`, `HuntingQuery`, `HuntingExecution`.
- **3.8.2: Safe Structured Threat Hunting Query DSL**:
  - Validates typed filters, operators, whitelist fields, bounded pagination. Prevents raw SQL injection.
- **3.8.3: Threat Hunting Detection Pack (10 Production Hunts)**:
  - `HUNT-001` to `HUNT-010` mapping to MITRE ATT&CK techniques with deterministic evidence extraction.
- **3.8.4: Investigation Case Management & Lifecycle**:
  - Full CRUD, state transitions, tags, notes, linked incidents, assets, users, and IOCs.
- **3.8.5: Evidence Correlation & Entity Pivoting**:
  - Cross-correlates multi-entity signals and generates directed investigation evidence graphs.
- **3.8.6: Explainable Behavioral Baseline Engine**:
  - Statistical deviation calculations (z-score, moving averages, baseline thresholds).
- **3.8.7: MITRE ATT&CK & Attack Graph & Risk Integration**:
  - Connects investigation cases to `MitreCoverageService`, `ThreatGraphService`, and `RiskScoringService`.
- **3.8.8: REST APIs & Strict RBAC**:
  - Endpoints under `/api/v1/hunting/*` and `/api/v1/investigations/*`.
- **3.8.9: Redis Stream & Asynchronous Hunting Worker**:
  - Integration with `sentinel:hunting` stream and group `sentinel:hunting:group`.
- **3.8.10: Performance Benchmarks, Security Tests & Full Regression**:
  - Latency benchmarks, RBAC boundary verification, and master 10-point release audit.

---

### 3. Safety, Security & Migration Strategy

- **Zero SQL / Command Injection**: Typed SQLAlchemy expressions only; strictly whitelist-filtered fields.
- **Fail-Closed Design**: Unsupported filters or operators are rejected with HTTP 400.
- **Backward Compatibility**: Preserves all existing Phase 3.0–3.7 endpoints, models, and tests.
