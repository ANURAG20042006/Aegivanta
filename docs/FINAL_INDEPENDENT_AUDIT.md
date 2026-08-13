# FINAL INDEPENDENT AUDIT — SENTINELAI
## Phase 11: External Examiner Review

**Audit Mode**: Independent — previous audit reports not trusted  
**Audit Timestamp**: 2026-08-13  
**Auditor Role**: External examiner, acting without prior assumptions  

---

## Executive Summary

SentinelAI is a well-engineered full-stack MLOps platform with production-quality security architecture, robust API design, and methodologically correct ML pipeline structure. **However, the underlying ML empirical performance is near-random (Macro F1 ≈ 0.02–0.07)** because the dataset generator creates class-independent synthetic features. This is a fundamental limitation that must not be obscured.

The engineering quality is high. The ML performance is poor. Both facts are reported honestly.

---

## 1. Fabrication Search

The following patterns were searched across `backend/`, `ml/`, `frontend/`, `scripts/`, `results/`:

| Pattern | Locations Found | Assessment |
|:---|:---|:---|
| `0.95` | `predict_service.py:220` | **Legitimate** — threshold for `HIGH_CONFIDENCE` alert, not a metric |
| `0.99` | Not found in runtime | Clean |
| `0.997` | Not found | Clean |
| Hardcoded SHAP | Not found — SHAP computed via `shap.TreeExplainer` | Clean |
| Fake ROC | `ml/artifacts/roc_curves.json` — values generated at training time | **Verified** — generated from real model evaluation |
| Fabricated dashboard values | Fixed in Phase 5 — dashboard calls `getSummary()` from DB | Clean |
| Static model confidence | `predict_service.py` uses `model.predict_proba()`, returns `None` if unsupported | Clean |
| **Fabricated research metrics** | `docs/RESEARCH_RESULTS.md` (Phase 7 walkthrough) reported F1=0.94 | **FOUND AND CORRECTED** in Phase 10 |

**Finding**: One fabrication detected — the Phase 7 `RESEARCH_RESULTS.md` contained placeholder metrics (F1=0.94) that did not match execution. This has been corrected to real values (F1=0.056) in Phase 10.

---

## 2. Artifact Audit

| Artifact | Path | Status |
|:---|:---|:---|
| `best_model.joblib` | `ml/artifacts/best_model.joblib` | ✅ Exists, 148 KB |
| `preprocessor.joblib` | `ml/artifacts/preprocessor.joblib` | ✅ Exists, 8.4 KB |
| `metadata.json` | `ml/artifacts/metadata.json` | ✅ Exists, real CV metrics |
| `artifact_manifest.json` | `ml/artifacts/artifact_manifest.json` | ✅ SHA256 hashes present |
| Feature count | `metadata.json: model_n_features_in=30` | ✅ Matches SelectKBest k=30 |
| Schema version | `schema-v1.0` | ✅ Consistent across manifest and metadata |
| Preprocessor hash | `1dffecc2e082...` | ✅ Present, used in rollback verification |
| Model hash | `b355179832...` | ✅ Present, used in rollback verification |

---

## 3. ML Methodology Verification

| Check | Result | Evidence |
|:---|:---|:---|
| Split-first | ✅ PASS | `train_pipeline.py: train_test_split()` called before any preprocessing |
| SMOTE inside folds only | ✅ PASS | `run_leakage_free_cv()` lines 83–97 — SMOTE inside loop |
| Feature selection inside folds only | ✅ PASS | `SelectKBest.fit_transform()` inside fold loop (line 81) |
| Validation fold never fitted | ✅ PASS | `.transform()` used on val fold, never `.fit_transform()` |
| Final test evaluated once | ✅ PASS | `evaluate_final_test_set()` called once after champion selection |
| Test metrics not in promotion gate | ✅ PASS | Promotion gate uses `cv_per_class_metrics` from training CV only |
| FPR = FP/(FP+TN) | ✅ PASS | `ml/metrics/fpr_calculator.py` implements correct formula |
| Missing FPR → rejection | ✅ PASS | Promotion gate fail-closed on `None` FPR |
| Missing latency → rejection | ✅ PASS | Promotion gate fail-closed on `None` latency |

---

## 4. Security Verification

| Check | Result | Evidence |
|:---|:---|:---|
| JWT authentication | ✅ PASS | All routes use `Depends(get_current_user)` |
| RBAC enforcement | ✅ PASS | Admin routes use `Depends(require_role("admin"))` |
| Production secret enforcement | ✅ PASS | `validate_production_settings()` raises on missing secrets |
| CORS wildcard prevented | ✅ PASS | `validate_production_settings()` checks `"*"` and localhost |
| Audit logging | ✅ PASS | `RequestTimingAndAuditMiddleware` logs all requests |
| No hardcoded secrets | ✅ PASS | Dev fallbacks use `{Role}_Secure2026!`, production requires env vars |
| Container non-root | ✅ PASS | Phase 9 fix — `adduser sentinelai` (UID 1001) |
| PostgreSQL not exposed | ✅ PASS | Phase 9 fix — changed from `ports` to `expose` |

---

## 5. Execution Evidence

### 5.1 Static Compilation
```
py -m compileall -q backend ml scripts tests
Exit code: 0 — 0 errors
```

### 5.2 Full Test Suite
```
py -m pytest -q
125 passed, 1 skipped, 12 warnings in 171.15s
Exit code: 0
```

### 5.3 Frontend Build
```
npm run build (in frontend/)
1582 modules transformed. Built in 3.43s.
Exit code: 0
```

### 5.4 Docker CLI
```
docker compose -f docker/docker-compose.yml config
SKIPPED — Docker CLI not installed on Windows test host
```

---

## 6. Empirical ML Performance (Real Numbers, Not Engineering Scores)

> These are the actual values from `ml/artifacts/metadata.json` and `results/baseline_comparison.csv`.

| Metric | CV (Decision Tree Champion) | Final Holdout Test |
|:---|:---|:---|
| Accuracy | 0.265 ± 0.053 | 0.160 |
| Macro F1-Score | **0.067 ± 0.021** | **0.020** |
| Precision (Macro) | 0.072 ± 0.020 | 0.036 |
| Recall (Macro) | 0.071 ± 0.022 | 0.014 |
| FPR (Macro) | 0.057 ± 0.001 | 0.057 |
| ROC-AUC | N/A | 0.479 |
| Inference Latency | — | 0.012 ms |

**Root Cause**: `ml/dataset/generator.py` generates features as independent random distributions regardless of class label. No classifier can learn anything from random noise. All models perform at roughly chance level (1/18 classes ≈ 0.056 Macro F1).

**This is not a pipeline bug.** The methodology is correct. The dataset has no signal.

---

## 7. Score Table

| Dimension | Score /10 | Rationale |
|:---|:---|:---|
| **Architecture** | **8.5/10** | Clear 5-layer architecture, async FastAPI, proper router separation, WebSocket support. Minor: no HTTPS in Docker |
| **ML Methodology** | **9/10** | Leakage-free CV, split-first SMOTE, proper FPR formula, holdout isolation — all correct |
| **Leakage Prevention** | **9.5/10** | Verified: scaler, selector, SMOTE all fitted inside folds. Split-first enforced. |
| **Model Selection** | **7/10** | Selection score formula is correct. Deducted: deep learning models are stubs, 18-class problem needs more candidates |
| **Inference** | **8/10** | Real model inference, real SHAP, confidence from `predict_proba`, fail-closed on missing artifacts |
| **MLOps** | **8.5/10** | Promotion gate with FPR/Recall/Latency checks, SHA256 rollback verification, audit logging, lifecycle states |
| **Security** | **9/10** | JWT, RBAC, production fail-closed, CORS validation, audit trail, non-root container. Minor: no HTTPS |
| **Backend/API** | **8.5/10** | 9 routers, real DB-backed responses, correlation headers, proper HTTP status codes, fail-closed on artifact missing |
| **Frontend** | **7.5/10** | Real API integration, dynamic mode badge, real predictions/SHAP display, ROC chart. Minor: bundle size warning |
| **XAI** | **8/10** | Real TreeExplainer, `available: false` when unsupported, timing measured, top-N extraction |
| **Drift Monitoring** | **8/10** | PSI + KS-test, SHA256 baseline hash, sliding window, no automatic promotion |
| **Testing** | **8.5/10** | 125 tests, 1 documented skip, covers leakage, security, API, XAI, drift |
| **Reproducibility** | **8/10** | Seeded training, `.env.example`, DEPLOYMENT.md, research suite script. Docker can't be tested without CLI |
| **Research Validity** | **5/10** | Methodology correct. Results near-random due to synthetic dataset. Phase 7 walkthrough contained fabricated values (corrected in Phase 10) |
| **Documentation** | **8.5/10** | Comprehensive docs updated with honest metrics. VIVA.md, ML_PIPELINE.md, RESEARCH.md all corrected |

### Weighted Overall: **8.1/10** (engineering)
### **Empirical ML Performance: POOR** (F1 ≈ 0.02–0.07 on synthetic dataset with no signal)

---

## 8. Issue Classification

### P0 (Submission Blocker) — None

### P1 (Major Issues)
| ID | Issue | Location | Recommendation |
|:---|:---|:---|:---|
| P1-1 | Synthetic dataset has no predictive signal — all models near-random | `ml/dataset/generator.py` | Replace with real CICIDS2017 CSV loader |
| P1-2 | Phase 7 walkthrough contained fabricated metrics (F1=0.94) | `docs/RESEARCH_RESULTS.md` | **Corrected in Phase 10** to real values |

### P2 (Moderate Issues)
| ID | Issue | Location | Recommendation |
|:---|:---|:---|:---|
| P2-1 | Deep learning models (1D-CNN, LSTM, Autoencoder) are untrained stubs | `ml/models/` | Implement with PyTorch/TensorFlow or remove |
| P2-2 | 12 Pydantic V2 deprecation warnings | `backend/app/schemas/auth.py`, `schemas/user.py` | Migrate `example=` to `json_schema_extra` |
| P2-3 | No HTTPS in Docker configuration | `docker/nginx.conf` | Add TLS termination with certbot/Let's Encrypt |
| P2-4 | Docker CLI not available for validation | CI/CD environment | Test in Docker-enabled environment |
| P2-5 | SQLite used in development (not production-safe) | `backend/app/config.py` | Enforced via `DATABASE_URL` env var |

### P3 (Minor Issues)
| ID | Issue | Location | Recommendation |
|:---|:---|:---|:---|
| P3-1 | Frontend bundle > 500 KB (Vite warning) | `frontend/dist/` | Code-split with dynamic imports |
| P3-2 | `double db.commit()` in `initialize_application()` | `backend/app/main.py:124–125` | Remove duplicate commit |
| P3-3 | `catboost_info/` directory committed to git | repo root | Add `catboost_info/` to `.gitignore` |

---

## 9. Final Verdict

**READY WITH MAJOR ISSUES**

### Justification
The project demonstrates **research-grade engineering and MLOps architecture** with:
- Correct and verifiable leakage-free cross-validation
- Production-quality security enforcement (JWT, RBAC, fail-closed secrets)
- Real SHAP explainability (not fabricated)
- Defensible promotion gate with SHA256 artifact integrity
- Comprehensive test coverage (125 tests)

However, it cannot receive a higher verdict because:
1. **P1-1**: The ML empirical performance is near-random. The platform is an excellent shell, but the core ML task (intrusion detection) does not work on this dataset
2. **P1-2** (Corrected): A fabricated F1=0.94 metric was found in the Phase 7 walkthrough — it has been corrected but reflects a research integrity failure that occurred during development

**If the real CICIDS2017 dataset were used** (replacing `ml/dataset/generator.py`), the system architecture is sound enough to achieve the F1 > 0.90 reported in the literature, and the verdict would be **RESEARCH-GRADE** or **EXCELLENT**.
