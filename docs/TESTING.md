# SentinelAI — Testing Guide

**Last Updated**: 2026-08-13

---

## 1. Test Suite Summary

| Category | Test Files | Tests |
|:---|:---|:---|
| ML Pipeline | `tests/ml/` | ~40 |
| Security & Auth | `tests/test_security*.py` | ~25 |
| API Endpoints | `tests/test_api*.py` | ~30 |
| XAI & Drift | `tests/test_drift_and_xai.py` | 6 |
| Integration | `tests/test_integration*.py` | ~20 |
| **Total** | | **125 passed, 1 skipped** |

---

## 2. Running the Test Suite

### Full Suite
```bash
py -m pytest -q
# Expected: 125 passed, 1 skipped, 12 warnings
```

### With Verbose Output
```bash
py -m pytest -v
```

### Specific Modules
```bash
py -m pytest tests/ml/ -v         # ML pipeline tests only
py -m pytest tests/test_security* -v   # Security tests only
```

---

## 3. ML Pipeline Tests (`tests/ml/`)

Key verified behaviors:

| Test | File | What It Verifies |
|:---|:---|:---|
| `test_split_before_smote` | `test_phase2_*.py` | Train/test split before SMOTE |
| `test_cv_isolation` | `test_phase2_*.py` | Validation fold not used in fitting |
| `test_fpr_formula` | `test_phase2_*.py` | FPR = FP/(FP+TN), not 1-recall |
| `test_missing_fpr_rejects` | `test_phase2_*.py` | Missing FPR → promotion rejected |
| `test_missing_latency_rejects` | `test_phase2_*.py` | Missing latency → promotion rejected |
| `test_final_test_not_in_promotion` | `test_phase2_*.py` | Final test metrics never reach promotion gate |
| `test_rollback_hash_mismatch` | `test_phase2_*.py` | Hash mismatch → rollback rejected |
| `test_shap_tree_explainer` | `test_drift_and_xai.py` | Real SHAP values returned |
| `test_drift_psi_detection` | `test_drift_and_xai.py` | PSI > 0.25 triggers DRIFT_DETECTED |

---

## 4. Intentional Skips

| Skip | Reason |
|:---|:---|
| 1 GPU benchmark test | Test host has no CUDA-capable GPU; guarded with `pytest.mark.skipif` |

---

## 5. Static Checks

```bash
# Python syntax compilation check
py -m compileall -q backend ml scripts tests
# Expected: 0 errors

# Frontend production build
cd frontend && npm run build
# Expected: 0 TypeScript errors, 0 build failures
```

---

## 6. Known Warnings

12 `PydanticDeprecatedSince20` warnings from `backend/app/schemas/auth.py` and `schemas/user.py` — using `example=` kwargs on `Field()` which is deprecated in Pydantic V2. These are non-breaking and will be cleaned up in a future schema refactor.
