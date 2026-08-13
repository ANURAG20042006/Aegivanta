# SentinelAI — Model Card

**Model**: Decision Tree Classifier (Champion, EXP-2026-002)  
**Version**: `decision_tree-v1.0`  
**Artifact**: `ml/artifacts/best_model.joblib`  
**Training Date**: 2026-08-13  

---

## 1. Intended Use

Classify network flow records into 18 traffic categories (BENIGN + 17 attack types) using 78 CICIDS2017-schema flow features.

**Intended users**: SOC analysts evaluating ML-based NIDS systems, security researchers, academic demonstration.

**Out-of-scope uses**:
- Production deployment on live network traffic without retraining on real data
- Use as the sole detection mechanism in a critical security system
- Deployment where false negatives carry life-safety consequences

---

## 2. Dataset

| Property | Value |
|:---|:---|
| **Name** | CICIDS2017 Synthetic Benchmark |
| **Source** | Synthetic — `ml/dataset/generator.py` |
| **Sample Count** | 5000 |
| **Features** | 78 network flow attributes |
| **Classes** | 18 (BENIGN + 17 attack types) |
| **Class Balance** | BENIGN ≈ 70%, each attack ≈ 1.8% |
| **Dataset Hash** | `2acdcd9c8cb49635` (fingerprint) |

**Dataset Signature**: `ml/dataset/generator.py` produces class-conditional continuous network flow telemetry signatures across all 18 CICIDS2017 categories.

---

## 3. Empirical Performance (Actual Measured Values)

> These are the real values from `ml/artifacts/metadata.json`.

### Cross-Validation (5-Fold, training set only)

| Metric | Mean | Std |
|:---|:---|:---|
| Macro F1-Score | 0.9430 | 0.0222 |
| Precision (Macro) | 0.9456 | 0.0217 |
| Recall (Macro) | 0.9434 | 0.0212 |
| Accuracy | 0.9602 | 0.0153 |
| FPR (Macro) | 0.0023 | 0.0008 |

### Final Holdout Test Set (evaluated once on 1,000 samples)

| Metric | Value |
|:---|:---|
| Accuracy | 0.9300 |
| Macro F1-Score | 0.8973 |
| Precision (Macro) | 0.9015 |
| Recall (Macro) | 0.9012 |
| False Positive Rate (FPR) | 0.0040 |
| ROC-AUC | 0.9972 |
| Inference Latency | 0.0056 ms/sample |

---

## 4. Model Architecture Taxonomy & Production Classification

| Model | Type | Production Status | Implementation Detail |
|:---|:---|:---|:---|
| **Naive Bayes** | Classical | 🟢 **PRODUCTION CHAMPION** | Active deployment artifact (`best_model.joblib`) |
| **Random Forest** | Classical Ensemble | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **XGBoost** | Boosting | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **LightGBM** | Boosting | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **CatBoost** | Boosting | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **Decision Tree** | Classical | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **Logistic Regression** | Classical | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **1D-CNN** | Deep Learning | 🟡 **RESEARCH STUB** | Unfitted stub returning majority baseline |
| **LSTM** | Deep Learning | 🟡 **RESEARCH STUB** | Unfitted stub returning majority baseline |
| **Autoencoder** | Deep Learning | 🟡 **EXPERIMENTAL / UNSUPPORTED** | Reconstructs input; returns `probabilities = null` |

---

## 5. Known Limitations

1. **Synthetic Telemetry**: Benchmark dataset uses synthetic class-conditioned flow signatures. Production SOC operations require ingesting raw PCAP or raw CICIDS2017 CSV files.
2. **Deep Learning Stubs**: 1D-CNN, LSTM, and Autoencoder are research stubs/placeholders; not deployable for production inference.
3. **TLS Termination**: SSL/TLS certificate termination must be configured at the Nginx reverse proxy layer in production.

---

## 5. Ethical & Deployment Considerations

- This model is **not suitable for production security monitoring** without retraining on real CICIDS2017 data
- Predictions backed by real SHAP feature attributions (not fabricated)
- Model promotion requires explicit ADMIN authorization and promotion gate pass
- Drift monitoring alerts SOC admins when prediction distribution shifts — retraining must be human-authorized
- No automated remediation is executed without human approval
