# SentinelAI — Phase 3.6 Architecture Specification

## Advanced Detection Intelligence & Automated Incident Correlation Engine

### 1. Architectural Overview

Phase 3.6 elevates SentinelAI from standalone telemetry inference and threat intelligence enrichment into an autonomous **Continuous Detection Intelligence & Incident Correlation Engine**. 

```
                                  +------------------------------+
                                  |  Raw Telemetry Flow Stream   |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  |  Fast Feature Normalization  |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  |   ML Threat Classification   |
                                  |  (CatBoost/LightGBM/Ensemble)|
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  | In-Memory Threat Intel Cache |
                                  |  (O(1) Hash / CIDR Matching) |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  | Modular Detection Rules (10) |
                                  | (RULE-001 through RULE-010)  |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  | Detection Correlation Engine |
                                  | (Sliding Windows & Grouping) |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  | Deterministic Risk Scoring   |
                                  |  (0–100 Explainable Formula) |
                                  +--------------+---------------+
                                                 |
                                                 v
                                  +------------------------------+
                                  | Incident Aggregation & Dedupl|
                                  | (Active Incidents / Timeline)|
                                  +--------------+---------------+
                                                 |
                                                 v
+-------------------------------+                |                +-------------------------------+
| Redis Stream sentinel:incidents<---------------+--------------->| REST API & Analyst Dashboard  |
+-------------------------------+                                 +-------------------------------+
```

---

### 2. Core Subsystems

#### 2.1 Detection Rule Framework (`backend/app/detection/`)
- Abstract base `DetectionRule` establishing mandatory `rule_id`, `name`, `severity`, `mitre_techniques`, and `evaluate(event, context)`.
- Global `DetectionRuleRegistry` providing high-throughput in-memory evaluation ($0.017\text{ ms/event}$).

#### 2.2 Continuous Detection Correlation (`backend/app/services/detection_correlation_service.py`)
- Ingests events and aggregates evidence across configurable sliding temporal windows (5m, 15m, 30m, 1h).
- Correlates by `(source_ip, destination_ip)`, `asset_id`, `ioc_value`, and `user_id`.
- Guarantees event idempotency and safe out-of-order event ordering.

#### 2.3 Incident Aggregation & Deduplication (`backend/app/services/incident_service.py`)
- Groups related detection clusters into unified `Incident` records, preventing alert fatigue and database explosion.
- Enforces strict finite state machine transitions (`OPEN`, `INVESTIGATING`, `CONTAINED`, `RESOLVED`, `CLOSED`, `FALSE_POSITIVE`).

#### 2.4 Deterministic Risk Scoring (`backend/app/services/risk_scoring_service.py`)
- Calculates a bounded $0 - 100$ risk score across 6 core weights (Severity 35%, Confidence 15%, Threat Intel 15%, Asset Criticality 15%, Lateral Movement 10%, Blast Radius 10%) with multi-event frequency multipliers.

#### 2.5 Automated Investigation Timeline (`backend/app/services/investigation_timeline_service.py`)
- Reconstructs chronological forensic event logs with attack progression summaries and dwell times.

#### 2.6 MITRE ATT&CK Matrix Coverage (`backend/app/services/mitre_coverage_service.py`)
- Computes real-time coverage percentages and technique frequency distributions against the Enterprise ATT&CK matrix.
