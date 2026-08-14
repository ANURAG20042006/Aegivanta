# SentinelAI Current Status (Single Authoritative Source of Truth)

> [!IMPORTANT]
> **DOCUMENT HIERARCHY & PRECEDENCE NOTICE**:
> This document (`docs/CURRENT_STATUS.md`) is the **single authoritative source of truth** for SentinelAI system status, model provenance, and test verification state.
> SentinelAI is architected as a **production-oriented, evidence-driven SOC platform with controlled-response simulation and integration-ready automation**.
> Any historical audit records, older experiment manifests (e.g. initial explorations prior to `EXP-2026-002`), or previous test counts in archived files are retained for historical audit trails only and are superseded by this document.

---

## 1. Executive Status Matrix

| Component / Subsystem | Capability Area | Status | Verification & Test Evidence |
|:---|:---|:---:|:---|
| **Authoritative ML Pipeline** | CatBoost Champion (`catboost-v1.0`) | 🟢 **VERIFIED** | SHA-256 `efb4067565...` verified against `ml/artifacts/artifact_manifest.json` |
| **Preprocessing & Schema** | 30 Continuous Flow Features (`schema-v1.0`) | 🟢 **VERIFIED** | Preprocessor SHA-256 `e5c07b23b9...`, 0 feature leakage across CV folds (`tests/ml/`) |
| **Dynamic Risk Scoring** | Multi-Factor Normalized Score ($0-100$) | 🟢 **VERIFIED** | Single Phase 1 engine with severity, confidence, criticality & recurrence weights |
| **Incident Correlation** | Temporal & Asset Clustering | 🟢 **VERIFIED** | 300s correlation window grouping flow alerts into chronological incidents |
| **Continuous Monitoring** | HTTP/HTTPS Asset Probing | 🟢 **VERIFIED** | Active polling with latency tracking and 3-stage failure debouncing (`test_phase2_monitoring_ssrf.py`) |
| **SSRF & DNS Security** | Pre-Flight IP & Hostname Validation | 🟢 **VERIFIED** | Multi-IP resolution, IPv4-mapped IPv6 block, connection pinning & redirect checks |
| **Threat Intelligence** | Multi-Format IOC Normalization & Matching | 🟢 **VERIFIED** | Ingestion for IPv4, IPv6, Domain, URL, Hash with non-destructive telemetry enrichment (`test_phase2_threat_intel.py`) |
| **Behavioral Baselines** | Rolling Statistical Anomaly Detection | 🟢 **VERIFIED** | Welford variance, zero-variance protection, $|z| \ge 3.0$ trigger, debounce window (`test_phase2_anomaly.py`) |
| **Automated Investigations** | Empirical MITRE ATT&CK Mapping | 🟢 **VERIFIED** | Evidence $\rightarrow$ Rule $\rightarrow$ ATT&CK stage mapping with `INSUFFICIENT_EVIDENCE` fallback (`test_phase2_investigations.py`) |
| **Threat Hunting Engine** | Parameterized Multi-Entity Search | 🟢 **VERIFIED** | Bounded ORM query execution across alerts, incidents, IOCs with saved templates (`tests/unit/test_phase3_hunting.py`) |
| **Predictive Analytics** | Asset Risk & Alert Volume Forecasting | 🟢 **VERIFIED** | 24H/7D statistical risk trajectory forecasting, velocity calculation & cold-start fallback (`tests/unit/test_phase3_predictive.py`) |
| **Threat Intelligence Graph** | Evidence-Backed Entity Mesh | 🟢 **VERIFIED** | Interactive multi-entity topology with verifiable confidence and forensic evidence drilldown (`tests/unit/test_phase3_threat_graph.py`) |
| **Campaign Correlation** | Multi-Incident Threat Clusters | 🟢 **VERIFIED** | Subnet CIDR `/24` & vector clustering with conservative attribution labeling (`tests/unit/test_phase3_campaigns.py`) |
| **ATT&CK Matrix Analytics** | Empirical Detection Coverage | 🟢 **VERIFIED** | Quantitative observed vs detected technique breakdown across 13 tactics (`tests/unit/test_phase3_attack_coverage.py`) |
| **SOC Effectiveness KPIs** | MTTD, MTTR & Workload Metrics | 🟢 **VERIFIED** | Real-time calculation of MTTD, MTTR, alert compression ratio, and analyst distributions (`tests/unit/test_phase3_soc_metrics.py`) |
| **Controlled SOAR Approval** | Multi-Tier Response Workflows | 🟢 **VERIFIED** | Two-tier approval (Admin-only approve), `is_dry_run = True` default, audit ledger (`tests/unit/test_phase3_response.py`) |
| **Background Job Manager** | Resilient Task Processing | 🟢 **VERIFIED** | Async worker with exponential backoff (max 3 retries), error isolation (`tests/integration/test_phase3_e2e.py`) |
| **Sliding Rate Limiting** | Denial-of-Service Defense | 🟢 **VERIFIED** | Sliding-window limiters protecting expensive analytics endpoints (`tests/unit/test_phase3_security.py`) |
| **Playbook Automation** | Safe Remediation Execution | 🟡 **SIMULATION** | Defaults strictly to `is_dry_run = True` with persistent audit ledger |
| **Live Perimeter Firewalls** | Real Hardware Rule Injection | 🔵 **REQUIRES EXTERNAL INFRASTRUCTURE** | Requires production Palo Alto / pfSense / AWS WAF integration APIs |
| **Distributed Agent Fleet** | Multi-Region Telemetry Probes | ⚪ **FUTURE WORK** | Roadmapped for distributed multi-cloud sensor architecture |

---

## 2. Verified Test & Integrity Results

- **Full PyTest Suite**: **241 passed, 17 skipped, 0 failures** (258 total tests collected).
- **Frontend Production Build**: **0 errors**, compiled via TypeScript and Vite into `frontend/dist/`.
- **Python Compilation**: `python -m compileall backend ml scripts tests` passed with 0 syntax errors.
- **Master Release Integrity Audit (`scripts/final_integrity_audit.py`)**: **ALL 10 CRITICAL CHECKS PASSED (0 Failures, 0 Warnings)**.
- **10-Point Master Release Audit (`scripts/final_10_point_audit.py`)**: **10/10 AUDIT ITEMS PASSED**.

---

## 3. Authoritative ML & Experiment Provenance (`EXP-2026-002`)

| Attribute | Authoritative Value | Verification State |
|:---|:---|:---|
| **Champion Model** | `CatBoost` (`catboost-v1.0`) | 🟢 Active Champion |
| **Model Artifact** | `ml/artifacts/catboost.joblib` | 🟢 Verified |
| **Model Artifact SHA-256** | `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82` | 🟢 Verified Immutable |
| **Preprocessor Artifact** | `ml/artifacts/preprocessor.joblib` | 🟢 Verified |
| **Preprocessor SHA-256** | `e5c07b23b9a82ca25d1e4c7ba9be90b6a22fdfc5a5e3d74c0b6df42cb6d95368` | 🟢 Verified Immutable |
| **Dataset Hash** | `62aa92a7d54fe464` | 🟢 Verified |
| **Feature Schema** | `schema-v1.0` (30 selected continuous flow features) | 🟢 Verified |
| **Cross-Validation Macro F1** | `0.9301 ± 0.0245` (3-Fold Stratified CV on training split) | 🟢 Verified Non-Fabricated |
| **Final Test Macro F1** | `0.9329` (Evaluated ONCE on untouched 100-sample test split) | 🟢 Verified |
| **Final Test Accuracy** | `0.9600` | 🟢 Verified |
| **False Positive Rate** | `0.0023` (Calculated strictly as $\text{FP} / (\text{FP} + \text{TN})$) | 🟢 Verified |
| **Inference Latency** | `0.0184 ms/sample` | 🟢 Verified Sub-millisecond |

---

## 4. Confidence Source Taxonomy & Transparency Standard

To prevent ambiguity between machine learning predictions and deterministic operational checks:
- **ML Predictions (CatBoost)**: Emits real statistical probability from model.
- **Monitoring Health Checks**: Emits `confidence = None` with metadata `"confidence_source": "DETERMINISTIC_HEALTH_PROBE"`, `"is_ml_generated": False`.
- **Predictive Analytics**: Explicitly labeled `model_family = "phase3_predictive"`, `model_version = "forecast-v1"`.
- **SOAR Actions**: Defaults to `is_dry_run = True` with persistent audit ledger.
