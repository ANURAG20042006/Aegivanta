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

**Critical limitation**: Features are generated as class-independent random distributions. There is **no predictive signal** in this dataset. Performance will be near-random on both training and test splits.

---

## 3. Empirical Performance (Actual Measured Values)

> These are the real values from `ml/artifacts/metadata.json` and `results/baseline_comparison.csv`. They are poor because the dataset has no signal.

### Cross-Validation (5-Fold, training set only)

| Metric | Mean | Std |
|:---|:---|:---|
| Macro F1-Score | 0.067 | 0.021 |
| Precision (Macro) | 0.072 | 0.020 |
| Recall (Macro) | 0.071 | 0.022 |
| Accuracy | 0.265 | 0.053 |
| FPR (Macro) | 0.057 | 0.001 |

### Final Holdout Test Set (evaluated once)

| Metric | Value |
|:---|:---|
| Accuracy | 0.16 |
| Macro F1-Score | 0.02 |
| Precision (Macro) | 0.0356 |
| Recall (Macro) | 0.0139 |
| False Positive Rate (FPR) | 0.0565 |
| ROC-AUC | 0.4787 |
| Inference Latency | 0.012 ms/sample |

---

## 4. Known Limitations

1. **No real signal**: Synthetic dataset → near-random performance on all models
2. **Poor minority class recall**: Most attack classes have 0% recall on test set
3. **Small dataset**: 5000 samples insufficient for 18-class classification
4. **Deep learning models not trained**: 1D-CNN, LSTM, Autoencoder return stub outputs only
5. **No real CICIDS2017 data**: Real CICIDS2017 dataset is 2.8 GB and not bundled

---

## 5. Ethical & Deployment Considerations

- This model is **not suitable for production security monitoring** without retraining on real CICIDS2017 data
- Predictions backed by real SHAP feature attributions (not fabricated)
- Model promotion requires explicit ADMIN authorization and promotion gate pass
- Drift monitoring alerts SOC admins when prediction distribution shifts — retraining must be human-authorized
- No automated remediation is executed without human approval
