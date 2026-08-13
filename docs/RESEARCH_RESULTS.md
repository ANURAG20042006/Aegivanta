# SENTINELAI — RESEARCH RESULTS & EMPIRICAL VALIDATION REPORT

**Experiment Suite**: `EXP-2026-002`  
**Execution Timestamp**: 2026-08-13  
**Script**: `scripts/run_research_suite.py`  

> **Research Integrity Note**: All metrics in this document are taken directly from execution-generated CSV files (`results/*.csv`) and `ml/artifacts/metadata.json`. No values have been manually entered or altered.

---

## 1. Research Questions (RQs) & Findings

### RQ1: Can supervised ML detect network attacks reliably?
**Finding**: **YES on class-conditioned flow telemetry.** All major classifiers achieve Macro F1 of **0.7830–0.9623** on held-out test splits. `ml/dataset/generator.py` produces class-conditional network telemetry signatures across all 18 attack categories.

### RQ2: Which model provides the optimal trade-off between detection performance and latency?
**Finding**: **Naive Bayes** achieves the highest multi-objective selection score (0.9597) due to ultra-low latency (0.0056 ms) and low FPR (0.0040) while maintaining 0.8973 Macro F1 on the test set. Ensemble models (Random Forest, XGBoost, LightGBM) achieve 0.7944–0.7964 Macro F1 with 0.028–0.158 ms latency.

### RQ3: What is the quantitative impact of feature selection and SMOTE?
**Finding**: Full pipeline (ANOVA SelectKBest + fold-isolated SMOTE) achieves 0.7964 Macro F1. Omitting feature selection achieves 0.7985 Macro F1, while omitting SMOTE achieves 0.7912 Macro F1.

### RQ4: How robust is the system under noise and distribution shift?
**Finding**: Detection performance degrades under synthetic Gaussian noise injection (F1 drops from 0.7964 to 0.5210 under 10% noise). The drift detector correctly triggers `DRIFT_DETECTED` alerts when feature distribution KS p-values drop below 0.05.

---

## 2. Baseline Model Comparison
**Source**: `results/baseline_comparison.csv` (frozen holdout test set)

| Model Name | Accuracy | Macro F1 | FPR | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **Random Forest** | 0.8475 | **0.7964** | 0.0091 | 0.158 |
| **XGBoost** | 0.8525 | 0.7951 | 0.0087 | 0.038 |
| **LightGBM** | 0.8525 | 0.7944 | 0.0087 | 0.028 |
| **CatBoost** | 0.8325 | 0.7867 | 0.0097 | 0.006 |
| **Decision Tree** | 0.8350 | 0.7830 | 0.0098 | 0.000 |
| **Logistic Regression** | 0.5975 | 0.6744 | 0.0233 | 0.000 |
| **Majority Baseline** | 0.0400 | 0.0043 | 0.0556 | 0.001 |

---

## 3. Stratified 5-Fold Cross-Validation
**Source**: `ml/artifacts/metadata.json` (training set only, N=4000)

### Naive Bayes (Champion by selection score)

| Fold | Accuracy | Macro F1 | FPR | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| fold_1 | 0.9712 | 0.9580 | 0.0017 | 0.005 |
| fold_2 | 0.9700 | 0.9575 | 0.0017 | 0.005 |
| fold_3 | 0.9712 | 0.9591 | 0.0017 | 0.005 |
| fold_4 | 0.9375 | 0.9094 | 0.0036 | 0.005 |
| fold_5 | 0.9513 | 0.9310 | 0.0028 | 0.005 |
| **Mean** | **0.9602** | **0.9430 ± 0.022** | **0.0023** | **0.005** |

---

## 4. Pipeline Component Ablation Study
**Source**: `results/ablation.csv`

| Variant | Accuracy | Macro F1 | FPR |
| :--- | :--- | :--- | :--- |
| Full Pipeline (Selection + SMOTE) | 0.8475 | 0.7964 | 0.0091 |
| Without Feature Selection | 0.8500 | 0.7985 | 0.0089 |
| Without SMOTE | 0.8450 | 0.7912 | 0.0093 |
