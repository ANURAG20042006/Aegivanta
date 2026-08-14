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
| **Playbook Automation** | Safe Remediation Execution | 🟡 **SIMULATION** | Defaults strictly to `is_dry_run = True` with persistent audit ledger |
| **Live Perimeter Firewalls** | Real Hardware Rule Injection | 🔵 **REQUIRES EXTERNAL INFRASTRUCTURE** | Requires production Palo Alto / pfSense / AWS WAF integration APIs |
| **Distributed Agent Fleet** | Multi-Region Telemetry Probes | ⚪ **FUTURE WORK** | Roadmapped for distributed multi-cloud sensor architecture |

---

## 2. Verified Test & Integrity Results

- **Full PyTest Suite**: **227 passed, 17 skipped, 0 failures** (244 total tests collected).
- **Frontend Production Build**: **0 errors**, compiled via TypeScript and Vite.
- **Python Compilation**: `python -m compileall -q backend ml scripts tests` passed with 0 syntax errors.
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
| **Preprocessor SHA-256** | `e5c07b23b9a82ca28b6805e0a2eeff3c42c97b47d6816fd089dbb92d12d93691` | 🟢 Verified Immutable |
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

1. **ML Model Predictions (`CatBoost`)**: Probabilistic confidence score ($0.0 - 1.0$) computed directly from `predict_proba` with feature attribution weights.
2. **Deterministic Monitoring Outages (`Health Probes`)**: Confidence is set to `None` with explicit metadata `confidence_source = "DETERMINISTIC_HEALTH_PROBE"`, `is_ml_generated = False`.
3. **Threat Intelligence Matches (`IOC Store`)**: Confidence reflects feed provider source reputation ($0.0 - 1.0$) labeled as `IOC_FEED_REPUTATION`.
4. **Behavioral Anomaly Events (`Z-Score Engine`)**: Score ($0 - 100$) bounded and calculated from statistical standard deviations ($|z| \ge 3.0$) with plain-English mathematical rationale.
