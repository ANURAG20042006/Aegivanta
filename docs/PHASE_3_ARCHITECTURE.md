# SentinelAI — Phase 3 Architecture Specification

**Status**: Verified & Active  
**Phase**: Phase 3 (Advanced SOC, Threat Hunting, Predictive Analytics & SOAR)  
**Authoritative Single Source**: `docs/CURRENT_STATUS.md`

---

## 1. Executive Architectural Summary

SentinelAI Phase 3 transforms the platform from a reactive detection and incident investigation engine into a **predictive, intelligence-driven, controlled-response Security Operations Center (SOC)** platform.

Phase 3 is built strictly as an **additive layer** on top of the immutable Phase 1 and Phase 2 foundations:
- The CatBoost champion model (`catboost-v1.0`, SHA-256: `efb4067565...`) remains the immutable primary ML flow classifier.
- The single Phase 1 `RiskScoringEngine` remains the sole authority for calculating numeric operational risk scores.
- Predictive forecasting, threat intelligence graphs, campaign correlation, and SOAR response workflows seamlessly integrate with existing assets, alerts, and incident timelines.

```
                    SENTINELAI UNIFIED ARCHITECTURE
                                   │
 ┌─────────────────────────────────┼────────────────────────────────┐
 │ PHASE 1: CORE DETECTION         │ PHASE 2: SOC WORKFLOWS         │ PHASE 3: ADVANCED SOC & SOAR
 │ • Flow Ingestion Engine         │ • Protected Assets             │ • Threat Hunting Engine
 │ • 30-Feature Preprocessor       │ • Continuous Monitoring (SSRF) │ • Predictive Risk Forecasts
 │ • CatBoost Champion ML          │ • Threat Intel Feeds (STIX)    │ • Threat Intelligence Graph
 │ • Single Risk Scoring Engine    │ • Behavioral Baselines/Spikes  │ • Campaign Correlation
 │ • Multi-Signal Correlator       │ • Automated Investigations     │ • Controlled SOAR Orchestrator
 │ • Incident Lifecycle State      │ • Playbook Sim Dry-Run         │ • MITRE ATT&CK Matrix Analytics
 └─────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

---

## 2. Core Phase 3 Subsystems

### 2.1 Parameterized Threat Hunting Engine (`HuntingService`)
- **Purpose**: Enables security analysts to conduct hypothesis-driven and indicator-driven investigations across security flow alerts, incidents, and threat intelligence IOCs.
- **Safety**: Uses parameterized SQLAlchemy ORM queries to prevent SQL injection vulnerabilities.
- **Features**:
  - Entity selection (`alerts`, `incidents`, `iocs`).
  - Time horizon bounding (`1h`, `24h`, `7d`, `30d`, custom).
  - Multi-attribute filtering (Source/Destination IP, CIDR, Attack Type, Severity).
  - Saved query templates for repeatable investigations.
  - Sub-millisecond execution timing and execution audit tracking (`HuntingExecution`).

### 2.2 Predictive Security Analytics (`PredictiveService`)
- **Purpose**: Computes forward-looking operational risk trajectories (24-hour and 7-day horizons) and enterprise alert volume projections.
- **Mathematical Grounding**:
  - Combines historical risk velocity, recent anomaly rates, health check states, and baseline score:
    $$\text{ForecastScore} = \text{Clamp}_{0}^{100}(\text{Baseline} + \Delta_{\text{alerts}} + \Delta_{\text{anomalies}} + \Delta_{\text{outages}})$$
  - Cold-start protection: Assets with $<3$ historical data points return baseline scores labeled `INSUFFICIENT_HISTORY` with confidence $\le 0.50$.
- **Predictive Model Independence**:
  - Model family is explicitly marked as `phase3_predictive` / `forecast-v1` / `volume-forecast-v1`.
  - Predictions are clearly presented as statistical projections, never masquerading as CatBoost ML probabilities.

### 2.3 Threat Intelligence Graph (`ThreatGraphService`)
- **Purpose**: Constructs an evidence-backed knowledge graph linking Protected Assets, Correlated Incidents, Security Flow Alerts, Threat IOCs, and MITRE ATT&CK Techniques.
- **Evidence Traceability Invariant**:
  - Every graph edge has an associated `evidence_count \ge 1` and verifiable confidence score.
  - Interactive drilldown allows analysts to inspect raw telemetry, IOC provenance, and MITRE chain details for every graph node.

### 2.4 Multi-Incident Campaign Correlation (`CampaignService`)
- **Purpose**: Correlates separate incidents across time and infrastructure into unified adversary campaign clusters.
- **Clustering Heuristics**:
  - Subnet CIDR `/24` infrastructure clustering.
  - Shared attack vector pattern clustering.
- **Attribution Invariant**:
  - Attribution is conservatively labeled as `UNKNOWN (Shared Infrastructure)` or `UNKNOWN (Pattern Correlation)` to avoid fabricating adversary threat actor names without external verifiable signatures.

### 2.5 Controlled SOAR / Safe Response Orchestration (`ResponseOrchestrator`)
- **Purpose**: Provides automated response orchestration with strict guardrails and human-in-the-loop authorization.
- **Safety Controls**:
  - Default execution mode is always `is_dry_run = True` (zero destructive modifications to perimeter infrastructure).
  - Two-tier authorization: Analysts submit requests; only `admin` role can approve remediation actions.
  - Permanent audit logging in `ResponseApproval` and `PlaybookExecution`.
  - Live execution requires explicit `force_live=True` flag and Admin confirmation.

### 2.6 MITRE ATT&CK Matrix & SOC Effectiveness Analytics (`AttackCoverageService` & `SOCMetricsService`)
- **ATT&CK Coverage**: Computes empirical matrix coverage across 13 enterprise tactics. Avoids overclaiming full coverage; clearly quantifies active vs unmonitored techniques.
- **SOC Metrics**: Computes Mean Time to Detect (MTTD), Mean Time to Respond (MTTR), Alert-to-Incident compression ratio, and analyst workload distribution.

---

## 3. Resilience & Security Architecture

### 3.1 Background Processing Resilience (`JobManager`)
- Telemetry batch syncs, threat feed ingestions, and health monitoring workers run with exponential backoff (up to 3 retries), timeout protection, and complete error isolation.
- Unhandled exceptions in background workers never crash core ML inference or API services.

### 3.2 In-Memory Rate Limiting (`core/rate_limit.py`)
- Sliding-window rate limiters protect expensive analytics endpoints:
  - Threat Hunting: 45 requests/min.
  - Predictive Analytics: 60 requests/min.
  - Threat Graph: 60 requests/min.

---

## 4. Verification & Invariants Matrix

| Subsystem / Metric | Target Specification | Empirical Verified Result | Status |
|---|---|---|---|
| **CatBoost Model** | SHA-256 `efb4067565...` | `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82` | **VERIFIED IMMUTABLE** |
| **Preprocessor** | SHA-256 `e5c07b23b9...` | `e5c07b23b9a82ca25d1e4c7ba9be90b6a22fdfc5a5e3d74c0b6df42cb6d95368` | **VERIFIED IMMUTABLE** |
| **PyTest Suite** | $\ge 227$ tests passing | **241 passed, 17 skipped, 0 failures** | **PASSED** |
| **Frontend Production Build** | TypeScript zero errors | Vite bundle built in 3.5s (0 errors) | **PASSED** |
| **10-Point Master Audit** | 10 / 10 items pass | **10 / 10 PASSED (0 FAILURES)** | **PASSED** |
| **Final Integrity Audit** | 10 / 10 checks pass | **ALL CRITICAL CHECKS PASSED** | **PASSED** |
