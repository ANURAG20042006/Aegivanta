# SentinelAI Current Status (Single Authoritative Source of Truth)

> [!IMPORTANT]
> **DOCUMENT HIERARCHY & PRECEDENCE NOTICE**:
> This document (`docs/CURRENT_STATUS.md`) is the **single authoritative source of truth** for SentinelAI system status, model provenance, and test verification state.
> Any historical audit records, older experiment manifests (e.g. initial explorations prior to `EXP-2026-002`), or previous test counts in archived files are retained for historical audit trails only and are superseded by this document.

---

## 1. Overall System Status: Phase 2 Released & Authoritatively Verified

- **Phase 1 Baseline Core**: Frozen & 100% Verified (CatBoost champion preserved, 30 features, zero regressions).
- **Phase 2 Intelligent Additive Layer**: Fully Implemented & Verified:
  - Enterprise SSRF-protected Continuous Monitoring with DNS rebinding defense & connection pinning.
  - Pluggable Threat Intelligence ingestion, normalization, and non-destructive telemetry enrichment.
  - Statistically grounded Behavioral Anomaly Engine with zero-variance protection and storm suppression.
  - Automated Investigations with empirical MITRE ATT&CK tactical mapping and `INSUFFICIENT_EVIDENCE` fallback.
  - Simulation-First Playbook Automation with strict RBAC and immutable audit logging.
- **Current PyTest Suite**: **216 passed, 17 skipped, 0 failures** (233 total test cases collected).
- **Frontend Production Build**: **0 errors**, production bundle compiled in 9.04s.
- **Master Release Audits**:
  - `scripts/final_integrity_audit.py`: **ALL CHECKS PASSED (0 Failures, 0 Warnings)**.
  - `scripts/final_10_point_audit.py`: **10/10 AUDIT ITEMS PASSED**.

---

## 2. Authoritative ML & Experiment Provenance (`EXP-2026-002`)

| Attribute | Authoritative Value | Verification State |
|:---|:---|:---|
| **Champion Model** | `CatBoost` (`catboost-v1.0`) | 🟢 Active Champion |
| **Model Artifact** | `ml/artifacts/catboost.joblib` | 🟢 Verified |
| **Model Artifact SHA-256** | `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82` | 🟢 Verified Immutable |
| **Preprocessor Artifact** | `ml/artifacts/preprocessor.joblib` | 🟢 Verified |
| **Preprocessor SHA-256** | `e5c07b23b9a82ca255c25ce426b3ca660d1338575001ff800bdf1fb1f2c96c46` | 🟢 Verified Immutable |
| **Dataset Hash** | `62aa92a7d54fe464` | 🟢 Verified |
| **Feature Schema** | `schema-v1.0` (30 selected continuous flow features) | 🟢 Verified |
| **Cross-Validation Macro F1** | `0.9301 ± 0.0245` (3-Fold Stratified CV on training split) | 🟢 Verified Non-Fabricated |
| **Final Test Macro F1** | `0.9329` (Evaluated ONCE on untouched test set) | 🟢 Verified |
| **Final Test Accuracy** | `0.9600` | 🟢 Verified |
| **False Positive Rate** | `0.0023` | 🟢 Verified FP / (FP + TN) |
| **Inference Latency** | `0.0184 ms/sample` | 🟢 Verified Sub-millisecond |

---

## 3. Confidence Source Taxonomy & Transparency Standard

To prevent ambiguity between machine learning predictions and deterministic operational checks:

1. **ML Model Predictions (`CatBoost`)**: Numeric confidence score ($0.0 - 1.0$) computed directly from `predict_proba` with feature attribution weights.
2. **Deterministic Monitoring Outages (`Health Probes`)**: Confidence source labeled as `DETERMINISTIC_HEALTH_PROBE` (`is_ml_generated = False`). No synthetic ML confidence score is attributed.
3. **Threat Intelligence Matches (`IOC Store`)**: Confidence reflects feed provider source reputation ($0.0 - 1.0$) labeled as `IOC_FEED_REPUTATION`.
4. **Behavioral Anomaly Events (`Z-Score Engine`)**: Score ($0 - 100$) bounded and calculated from statistical standard deviations ($|z| \ge 3.0$) with plain-English mathematical rationale.
