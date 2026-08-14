# SentinelAI Current Status (Single Authoritative Source of Truth)

> [!IMPORTANT]
> **DOCUMENT HIERARCHY & PRECEDENCE NOTICE**:
> This document (`docs/CURRENT_STATUS.md`) is the **single authoritative source of truth** for SentinelAI system status, model provenance, and test verification state.
> Any historical audit records, older experiment manifests (e.g. initial explorations prior to `EXP-2026-002`), or previous test counts in archived files are retained for historical audit trails only and are superseded by this document.

---

## 1. Executive Status Matrix

| Component / Subsystem | Capability Area | Status | Verification & Evidence |
|:---|:---|:---:|:---|
| **Authoritative ML Pipeline** | CatBoost Champion (`catboost-v1.0`) | 🟢 **VERIFIED** | SHA-256 `efb4067565...` verified against `ml/artifacts/artifact_manifest.json` |
| **Preprocessing & Schema** | 30 Continuous Flow Features (`schema-v1.0`) | 🟢 **VERIFIED** | Preprocessor SHA-256 `e5c07b23b9...`, 0 feature leakage across CV folds |
| **Dynamic Risk Scoring** | Multi-Factor Normalized Score ($0-100$) | 🟢 **VERIFIED** | Single Phase 1 engine with severity, confidence, criticality & recurrence weights |
| **Incident Correlation** | Temporal & Asset Clustering | 🟢 **VERIFIED** | 300s correlation window grouping flow alerts into chronological incidents |
| **Continuous Monitoring** | HTTP/HTTPS Asset Probing | 🟢 **VERIFIED** | Active polling with latency tracking and 3-stage failure debouncing |
| **SSRF & DNS Security** | Pre-Flight IP & Hostname Validation | 🟢 **VERIFIED** | Multi-IP resolution, IPv4-mapped IPv6 block, connection pinning & redirect checks |
| **Threat Intelligence** | Multi-Format IOC Normalization & Matching | 🟢 **VERIFIED** | Ingestion for IPv4, IPv6, Domain, URL, Hash with non-destructive telemetry enrichment |
| **Behavioral Baselines** | Rolling Statistical Anomaly Detection | 🟢 **VERIFIED** | Welford variance, zero-variance protection, $|z| \ge 3.0$ trigger, debounce window |
| **Automated Investigations** | Empirical MITRE ATT&CK Mapping | 🟢 **VERIFIED** | Evidence $\rightarrow$ Rule $\rightarrow$ ATT&CK stage mapping with `INSUFFICIENT_EVIDENCE` fallback |
| **Threat Hunting Engine** | Parameterized Multi-Entity Search | 🟢 **VERIFIED (PHASE 3)** | Fast bounded query execution across alerts, incidents, IOCs with saved query templates |
| **Predictive Risk Analytics** | Asset Risk & Volume Forecasting | 🟢 **VERIFIED (PHASE 3)** | 24H/7D statistical risk trajectory forecasting, volume projections & cold-start fallback |
| **Threat Intelligence Graph** | Evidence-Backed Entity Mesh | 🟢 **VERIFIED (PHASE 3)** | Interactive multi-entity topology with verifiable confidence and forensic evidence drilldown |
| **Campaign Correlation** | Multi-Incident Threat Clusters | 🟢 **VERIFIED (PHASE 3)** | Subnet CIDR & vector clustering with conservative attribution labeling |
| **Controlled SOAR** | Multi-Tier Response Workflows | 🟢 **VERIFIED (PHASE 3)** | Two-tier approval (Admin-only approve), `is_dry_run = True` default, full audit ledger |
| **MITRE Matrix Analytics** | Empirical Detection Coverage | 🟢 **VERIFIED (PHASE 3)** | Quantitative observed vs detected technique breakdown across 13 tactics |
| **SOC Effectiveness KPIs** | MTTD, MTTR & Workload Metrics | 🟢 **VERIFIED (PHASE 3)** | Real-time calculation of MTTD, MTTR, alert compression ratio, and analyst distributions |
| **Live Hardware Firewalls** | Real Hardware Rule Injection | 🔵 **REQUIRES EXTERNAL INFRASTRUCTURE** | Requires production Palo Alto / pfSense / AWS WAF integration APIs |
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
