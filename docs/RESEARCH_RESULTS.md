# SENTINELAI — RESEARCH RESULTS & EMPIRICAL VALIDATION REPORT

**Experiment Suite**: `EXP-2026-002`  
**Execution Timestamp**: 2026-08-13  
**Script**: `scripts/run_research_suite.py`  

> **Research Integrity Note**: All metrics in this document are taken directly from execution-generated CSV files (`results/*.csv`) and `ml/artifacts/metadata.json`. No values have been manually entered or altered. Some metrics differ significantly from the Phase 7 walkthrough, which contained fabricated placeholder numbers. This document is the authoritative corrected version.

---

## 1. Research Questions (RQs) & Findings

### RQ1: Can supervised ML detect network attacks reliably?
**Finding**: **NOT on this synthetic dataset.** All classifiers achieve Macro F1 of 0.02–0.07, which is near-random performance. The root cause is that `ml/dataset/generator.py` generates features as class-independent random distributions — there is no predictive signal. On the real CICIDS2017 dataset, the literature reports F1 > 0.95 for Random Forest.

### RQ2: Which model provides the optimal trade-off between detection performance and latency?
**Finding**: XGBoost achieves the best Macro F1 (0.0626) on the baseline comparison with low latency (0.013 ms). However, all models perform comparably near-random, making this comparison largely meaningless on this dataset.

### RQ3: What is the quantitative impact of feature selection and SMOTE?
**Finding**: On this synthetic dataset, removing SMOTE and feature selection slightly increases accuracy (from 0.52 to 0.72) because models without rebalancing learn to predict the majority class (BENIGN=70%) more aggressively. F1 scores remain near-random across all ablation variants.

### RQ4: How robust is the system under noise and distribution shift?
**Finding**: Performance degrades further under Gaussian noise as expected. The drift detector correctly triggers `DRIFT_DETECTED` alerts at high noise levels. See `results/robustness.csv` for per-noise-level results.

---

## 2. Baseline Model Comparison
**Source**: `results/baseline_comparison.csv` (frozen holdout test set, N=400 samples)

| Model Name | Accuracy | Macro F1 | FPR | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| LightGBM | 0.6125 | 0.0502 | 0.0579 | 0.042 |
| XGBoost | 0.490 | **0.0626** | 0.0569 | 0.013 |
| **Random Forest** | 0.545 | 0.0487 | 0.0565 | 0.065 |
| CatBoost | 0.335 | 0.051 | 0.0559 | 0.008 |
| Decision Tree | 0.223 | 0.034 | 0.055 | 0.000 |
| Logistic Regression | 0.030 | 0.040 | 0.055 | 0.000 |
| Majority Baseline | 0.020 | 0.002 | 0.056 | 0.001 |

---

## 3. Stratified 5-Fold Cross-Validation
**Source**: `results/cross_validation.csv` (training set only, N=4000)

### Random Forest (Champion by selection score)

| Fold | Accuracy | Macro F1 | FPR | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| fold_1 | 0.535 | 0.0619 | 0.054 | 3.922 |
| fold_2 | 0.575 | 0.0516 | 0.054 | 3.944 |
| fold_3 | 0.548 | 0.0614 | 0.055 | 4.129 |
| fold_4 | 0.535 | 0.0404 | 0.057 | 4.037 |
| fold_5 | 0.548 | 0.0646 | 0.055 | 4.428 |
| **Mean** | **0.548** | **0.0560 ± 0.009** | **0.055** | **4.09** |

---

## 4. Pipeline Component Ablation Study
**Source**: `results/ablation.csv`

| Ablation Variant | Accuracy | Macro F1 | FPR |
| :--- | :--- | :--- | :--- |
| Full Pipeline (Selection + SMOTE) | 0.518 | 0.040 | 0.056 |
| Without Feature Selection | 0.668 | 0.045 | 0.056 |
| Without SMOTE Balancing | 0.715 | 0.046 | 0.056 |

---

## 5. Generated Visualizations
- `results/plots/f1_vs_fpr.png`: F1-Score vs FPR trade-off across candidate models
- `results/plots/latency_comparison.png`: Per-sample inference latency (ms)
- `results/plots/ablation_study.png`: Pipeline component ablation comparison

---

## 6. Research Integrity Verification

- **Test Set Isolation**: Test set frozen before any model training. Never used for hyperparameter tuning or model selection. ✓
- **CV Isolation**: 5-Fold CV executed on training set only. ✓
- **No Fabricated Metrics**: All values sourced from actual CSV execution. See `results/*.csv`. ✓
- **Limitation Disclosed**: Synthetic dataset with no class-conditional signal. ✓

---

## 7. Corrected From Phase 7 Walkthrough

The Phase 7 walkthrough document contained fabricated metrics (Macro F1 ≈ 0.94). Those numbers were placeholders and do not reflect actual execution. The correct values are in this document and traceable to `results/*.csv` and `ml/artifacts/metadata.json`.
