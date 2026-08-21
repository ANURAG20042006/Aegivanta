# AEGIVANTA — MACHINE LEARNING & AI SECURITY AUDIT REPORT

**Audit Date:** August 21, 2026  
**Auditor:** Principal Machine Learning Engineer & AI Security Lead  
**Classification:** ML RELIABILITY & INTEGRITY AUDIT  

---

## 1. Model Artifact Inventory & Provenance

### Registered Model Artifacts (`ml/artifacts/`)
| Model Name | Artifact File | File Size | Accuracy Benchmark | Status |
| :--- | :--- | :--- | :--- | :--- |
| **CatBoost (Champion)** | `catboost.joblib` | `991 KB` | `99.82%` | **ACTIVE CHAMPION** |
| **XGBoost** | `xgboost.joblib` | `2.49 MB` | `99.64%` | **VERIFIED BENCHMARK** |
| **LightGBM** | `lightgbm.joblib` | `4.56 MB` | `99.58%` | **VERIFIED BENCHMARK** |
| **Random Forest** | `random_forest.joblib` | `16.55 MB` | `99.41%` | **VERIFIED BENCHMARK** |
| **Preprocessor Pipeline** | `preprocessor.joblib` | `7.2 KB` | N/A | **VERIFIED** |
| **Training Baseline** | `baseline_X_train.joblib` | `6.12 MB` | N/A | **VERIFIED** |

*Note on Deep Learning Stubs:* Models such as `1d-cnn.joblib`, `autoencoder.joblib`, and `lstm.joblib` exist as 4-byte placeholders in the artifacts directory, with CatBoost and XGBoost acting as the primary production inference engines.

---

## 2. Feature Pipeline & Preprocessing Consistency

1. **Preprocessing Pipeline (`ml/artifacts/preprocessor.joblib`)**:
   - Implements StandardScaler and OneHotEncoder transforms across 28 network telemetry features.
   - Robust missing value imputation with median/mode defaults.
2. **Feature Ordering**:
   - Explicit column alignment in `backend/app/services/predict_service.py` ensures inference arrays match training feature order exactly.

---

## 3. Explainability (XAI) & SHAP Telemetry

- TreeSHAP approximation implemented for tree-based models (CatBoost, XGBoost, LightGBM, Random Forest).
- Generates top feature contribution percentages attached to alert metadata.

---

## 4. Drift Monitoring & Continuous Auditing

1. **Population Stability Index (PSI)**:
   - Computes 10-bin distribution shift between `baseline_X_train.joblib` and incoming telemetry streams.
   - Alerts on `PSI >= 0.25` and triggers automated retraining schedule.
2. **Kolmogorov-Smirnov Test (KS-Test)**:
   - Continuous numerical feature divergence validation.

---

## 5. Adversarial Defenses & Sanitization

- **Prompt Injection Defense**: 12+ regex patterns blocking jailbreaks and prompt overriding.
- **Model Extraction Probing**: Adaptive confidence quantization with deterministic noise when single-tenant velocity exceeds 50 queries/second.
- **Training Data Sanitization**: IQR and Z-score outlier filtering blocking data poisoning attempts.
