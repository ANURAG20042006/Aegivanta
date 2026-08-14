# SentinelAI — Testing Guide

**Last Updated**: 2026-08-14

---

## 1. Test Suite Summary

| Category | Scope / Directory | Tests |
|:---|:---|:---|
| ML & Provenance | `tests/ml/` | 50+ |
| Security, Auth & RBAC | `tests/test_security*.py`, `tests/security/` | 30+ |
| API Endpoints & Health | `tests/api/`, `tests/test_backend_api_integrity.py` | 40+ |
| XAI & Drift | `tests/test_drift_and_xai.py` | 6 |
| Phase 1 SOC End-to-End | `tests/integration/` | 30+ |
| **Total Test Count** | **Full Pytest Suite** | **193 passed, 17 skipped, 0 failed (210 collected)** |

---

## 2. Running the Test Suite

### Full Suite
```bash
python -m pytest -q
# Expected: 193 passed, 17 skipped, 0 failed
```

### With Verbose Output
```bash
python -m pytest -v
```

### Specific Focus Modules
```bash
python -m pytest tests/ml/ -v                              # ML pipeline tests only
python -m pytest tests/test_security_rbac_hardening.py -v   # Security & RBAC tests only
python -m pytest tests/integration/test_complete_soc_pipeline.py -v  # Phase 1 SOC E2E tests
```

---

## 3. ML Pipeline & Research Integrity Tests

Key verified behaviors:

| Test | Module | What It Verifies |
|:---|:---|:---|
| `test_split_before_smote` | `tests/ml/` | Train/test split executed before SMOTE |
| `test_cv_isolation` | `tests/ml/` | Validation folds strictly isolated during fitting |
| `test_fpr_formula` | `tests/test_fpr.py` | FPR = FP/(FP+TN), not 1-recall |
| `test_final_test_not_in_promotion` | `tests/ml/` | Final test metrics never reach promotion gate |
| `test_shap_tree_explainer` | `tests/test_drift_and_xai.py` | Real SHAP values returned from model |
| `test_drift_psi_detection` | `tests/test_drift_and_xai.py` | PSI calculation and alert triggering |
| `test_16_step_complete_operational_pipeline` | `tests/integration/` | Full telemetry -> ML -> asset matching -> risk -> alert -> correlation -> timeline -> WebSocket |

---

## 4. Intentional Skips

| Skips | Reason |
|:---|:---|
| 17 GPU / long-running benchmark tests | Test host environment has no CUDA-capable GPU or tests are marked for nightly benchmarks; guarded with `@pytest.mark.skipif`. |

---

## 5. Static & Integrity Audits

```bash
# Python syntax compilation check
python -m compileall -q backend ml scripts tests
# Expected: 0 errors

# Master 10-Point Release Audit
python scripts/final_10_point_audit.py
# Expected: ALL 10 AUDIT ITEMS PASSED (0 FAILURES)

# Final Integrity Audit
python scripts/final_integrity_audit.py
# Expected: ALL CRITICAL CHECKS PASSED

# Frontend production build
cd frontend && npm run build
# Expected: 0 TypeScript errors, 0 build failures
```
