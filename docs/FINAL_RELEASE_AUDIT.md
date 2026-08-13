# SentinelAI — Final Release Audit & Evidence Matrix

**Audit Type**: Release Candidate (RC) Clean-Environment Hardening Audit  
**Audit Date**: 2026-08-13  
**Auditor**: Senior Architecture & QA Integrity Auditor  
**Execution Environment**: Python 3.11.5 | Windows 10 | React 18 + Vite 5  

---

## 1. Clean Environment & Dependency Verification

- **Python Version**: `3.11.5`
- **scikit-learn Version**: `1.6.1` (satisfies `scikit-learn>=1.6,<1.7` constraint)
- **aiosqlite Version**: `0.22.1`
- **Dependency Audit (`scripts/verify_environment.py`)**:
  ```text
  RESULT: ALL REQUIRED DEPENDENCIES VERIFIED OK (23/23 packages verified)
  ```

---

## 2. Test Suite Execution Summary

- **Command Executed**: `python -m pytest -q`
- **Collection Errors**: `0`
- **Tests Passed**: `129`
- **Tests Failed**: `0`
- **Tests Skipped**: `1`
- **Execution Duration**: `143.74 seconds`
- **Status**: ✅ **100% PASS**

---

## 3. Machine Learning & Artifact Integrity Audit

- **Authoritative Model Artifact**: `ml/artifacts/best_model.joblib`
- **Authoritative Preprocessor Artifact**: `ml/artifacts/preprocessor.joblib`
- **Model Feature Count (`n_features_in_`)**: `30`
- **Preprocessor Selected Features (`selected_feature_names`)**: `30`
- **Dimension Agreement**: `30 == 30` (✅ **EXACT MATCH**)
- **Artifact Manifest Verification (`artifact_manifest.json`)**:
  - Model SHA256: `5a01833d72ed2ec5...` (✅ **HASH MATCH**)
  - Preprocessor SHA256: `e5c07b23b9a82ca2...` (✅ **HASH MATCH**)
  - Feature Schema Version: `schema-v1.0`

---

## 4. Empirical ML Metrics Disclosure (Authoritative Experiment: EXP-2026-002)

- **Authoritative Source**: `ml/artifacts/metadata.json` (Experiment ID: `EXP-2026-002`)
- **Benchmark Dataset**: `synthetic_cicids2017_benchmark`
- **Dataset Size**: `5,000` samples, `82` features (78 flow telemetry + metadata)
- **Class Taxonomy**: `18` classes (`BENIGN` + 17 attack categories)
- **5-Fold Cross-Validation Metrics (TRAIN split only, N=4,000)**:
  - Macro F1 Mean: `0.9430 ± 0.0222`
  - Precision Mean: `0.9456 ± 0.0217`
  - Recall Mean: `0.9434 ± 0.0212`
  - Accuracy Mean: `0.9602 ± 0.0153`
  - Macro FPR: `0.0023 ± 0.0008`
- **Final Holdout Test Evaluation (Evaluated ONCE on 20% untouched test set, N=1,000)**:
  - Accuracy: `0.9300`
  - Macro F1: `0.8973`
  - Precision: `0.9015`
  - Recall: `0.9012`
  - Macro FPR: `0.0040`
  - ROC-AUC: `0.9972`
  - Inference Latency: `0.0056 ms/sample`

---

## 5. Security & Secret Management Verification

- **Default Credential Elimination**:
  - `backend/app/main.py` and `backend/app/reset_users.py` contain zero hardcoded fallback passwords.
  - Fail-closed startup (`RuntimeError`) if `SENTINEL_ADMIN_PASSWORD`, `SENTINEL_ANALYST_PASSWORD`, or `SENTINEL_VIEWER_PASSWORD` environment variables are absent.
  - `tests/conftest.py` injects isolated test credentials via `os.environ.setdefault()` during pytest.
- **Rollback Security Verification**:
  - 12-point integrity check verifies registered model SHA256 checksum and feature dimension compatibility prior to active model state mutation.

---

## 6. Frontend Build Verification

- **Command Executed**: `cd frontend && npm run build`
- **Vite Version**: `v5.4.21`
- **Modules Transformed**: `1582`
- **Build Duration**: `3.10 seconds`
- **Output Artifact**: `frontend/dist/index.html` (✅ **CLEAN BUILD**)

---

## 7. System Integrity Audit Output

- **Command Executed**: `python scripts/final_integrity_audit.py`
- **Critical Failures**: `0`
- **Warnings**: `0`
- **Audit Result**: `ALL CRITICAL CHECKS PASSED` (Exit code 0)

---

## 8. Disclosed Limitations

1. **Synthetic Telemetry Signals**: `CICIDS2017DataGenerator` synthesizes continuous flow telemetry signatures. Enterprise SOC production deployment requires ingesting raw real-world PCAP or raw CICIDS2017 CSV files.
2. **TLS Proxying**: Nginx proxying is configured for HTTP port 80. Production HTTPS TLS termination (Certbot / SSL certs) must be provided at the reverse proxy layer as documented in `docs/DEPLOYMENT.md`.
