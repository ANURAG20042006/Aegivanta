# SentinelAI — Model Card

**Model**: CatBoost Classifier (Champion, EXP-2026-002)  
**Version**: `catboost-v1.0`  
**Artifact**: `ml/artifacts/catboost.joblib` / `ml/artifacts/best_model.joblib`  
**Artifact SHA-256**: `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82`  
**Training Date**: 2026-08-13  

---

## 1. Intended Use

Classify network flow records into 18 traffic categories (BENIGN + 17 attack types) using 30 selected continuous flow features from the CICIDS2017 schema.

**Intended users**: SOC analysts evaluating ML-based NIDS systems, security researchers, enterprise SOC teams.

**Out-of-scope uses**:
- Production deployment on live network traffic without retraining on real data
- Use as the sole detection mechanism in a critical security system without human analyst oversight
- Deployment where false negatives carry life-safety consequences

---

## 2. Dataset

| Property | Value |
|:---|:---|
| **Name** | `synthetic_cicids2017_benchmark` |
| **Source** | Synthetic class-conditional telemetry — `ml/dataset/generator.py` |
| **Sample Count** | 500 total (train: 400 raw / 2,574 post-SMOTE, test: 100) |
| **Selected Features** | 30 selected network flow attributes |
| **Classes** | 18 (BENIGN + 17 attack types) |
| **Class Balance** | Stratified across all 18 categories |
| **Dataset Hash** | `62aa92a7d54fe464` |

---

## 3. Empirical Performance (Authoritative Measured Values)

> Derived directly from `results/EXP-2026-002/provenance.json` and `ml/artifacts/metadata.json`.

### Cross-Validation (3-Fold Stratified, training set only)

| Metric | Mean | Std |
|:---|:---|:---|
| Macro F1-Score | **0.9301** | 0.0245 |
| Precision (Macro) | 0.9405 | 0.0190 |
| Recall (Macro) | 0.9323 | 0.0292 |
| Accuracy | 0.9625 | 0.0148 |
| FPR (Macro) | 0.0022 | 0.0008 |

### Final Holdout Test Set (evaluated once on 100 held-out samples)

| Metric | Value |
|:---|:---|
| Accuracy | **0.9600** |
| Macro F1-Score | **0.9329** |
| Precision (Macro) | 0.9333 |
| Recall (Macro) | 0.9389 |
| False Positive Rate (FPR) | **0.0023** |
| ROC-AUC | **0.9996** |
| Authoritative Inference Latency | **0.0184 ms/sample** |
| Comparative Benchmark Latency | 0.0086 ms/sample |

---

## 4. Model Architecture Taxonomy & Production Classification

| Model | Type | Production Status | Implementation Detail |
|:---|:---|:---|:---|
| **CatBoost** | Boosting | 🟢 **PRODUCTION CHAMPION** | Active deployment artifact (`catboost.joblib` / `best_model.joblib`) |
| **Random Forest** | Classical Ensemble | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **XGBoost** | Boosting | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **LightGBM** | Boosting | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **Decision Tree** | Classical | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **Naive Bayes** | Classical | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **Logistic Regression** | Classical | 🟢 **PRODUCTION QUALIFIED** | Evaluated via ModelSelectorSuite |
| **1D-CNN** | Deep Learning | 🟡 **RESEARCH STUB** | Unfitted stub returning majority baseline |
| **LSTM** | Deep Learning | 🟡 **RESEARCH STUB** | Unfitted stub returning majority baseline |
| **Autoencoder** | Deep Learning | 🟡 **EXPERIMENTAL / UNSUPPORTED** | Reconstructs input; returns `probabilities = null` |

---

## 5. Ethical & Deployment Considerations

- Predictions backed by real SHAP TreeExplainer feature attributions (not fabricated)
- Model promotion requires explicit ADMIN authorization and promotion gate pass
- Drift monitoring alerts SOC analysts when prediction distribution shifts
- No automated remediation is executed without human approval
