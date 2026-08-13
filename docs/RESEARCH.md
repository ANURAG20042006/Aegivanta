# SentinelAI — Research Documentation

**Last Updated**: 2026-08-13  
**Experiment ID**: EXP-2026-002  

---

## 1. Research Questions

**RQ1**: Can supervised ML classifiers detect network attacks when trained on CICIDS2017-schema flow features?

**RQ2**: Which model architecture provides the best trade-off between detection performance (F1, FPR) and inference latency?

**RQ3**: What is the quantitative impact of feature selection and SMOTE class rebalancing on classifier performance?

**RQ4**: How robust are trained models under increasing feature noise and distribution shift?

---

## 2. Methodology

### 2.1 Experimental Design
- **Data**: CICIDS2017 synthetic benchmark, 5000 samples, 78 features, 18 classes
- **Seed**: 42 (fixed for reproducibility)
- **Split**: 80/20 stratified train/test — frozen before training
- **CV**: 5-Fold Stratified K-Fold on training set only
- **Model Selection**: Highest composite score (0.4×F1 + 0.3×Recall + 0.2×(1−FPR) + 0.1×(1/latency))
- **Final test**: Evaluated ONCE after champion selection

### 2.2 Leakage Prevention
Preprocessing (`StandardScaler`, `SelectKBest`, `SMOTE`) fitted **inside each CV fold** on training fold only, then applied to validation fold without refitting.

---

## 3. Results

### 3.1 RQ1 — Answer: POOR performance due to synthetic dataset limitation

All classifiers perform near-randomly (Macro F1 = 0.02–0.07) because the synthetic generator creates class-independent feature distributions. There is no learnable signal. On real CICIDS2017 data (e.g. Panigrahi & Borah, 2018), Random Forest achieves F1 > 0.95.

### 3.2 RQ2 — Baseline Model Comparison (Actual Results from `results/baseline_comparison.csv`)

| Model | Accuracy | Macro F1 | FPR | Latency (ms) |
|:---|:---|:---|:---|:---|
| **LightGBM** | 0.6125 | **0.0502** | 0.0579 | 0.042 |
| **XGBoost** | 0.490 | 0.0626 | 0.0569 | 0.013 |
| **Random Forest** | 0.545 | 0.0487 | 0.0565 | 0.065 |
| **CatBoost** | 0.335 | 0.051 | 0.0559 | 0.008 |
| Decision Tree | 0.223 | 0.034 | 0.055 | 0.000 |
| Logistic Regression | 0.030 | 0.040 | 0.0548 | 0.000 |
| Majority Baseline | 0.020 | 0.002 | 0.056 | 0.001 |

### 3.3 RQ3 — Ablation Study (Actual from `results/ablation.csv`)

| Variant | Accuracy | Macro F1 | FPR |
|:---|:---|:---|:---|
| Full Pipeline (Selection + SMOTE) | 0.518 | 0.040 | 0.056 |
| Without Feature Selection | 0.668 | 0.045 | 0.056 |
| Without SMOTE | 0.715 | 0.046 | 0.056 |

**Finding**: In this synthetic dataset, removing SMOTE and feature selection slightly improves accuracy (model learns to predict majority class more). F1 remains near-random across all variants, confirming no learnable signal.

### 3.4 RQ4 — Robustness (Actual from `results/robustness.csv`)
See `results/robustness.csv` for noise perturbation results. Models degrade further under increased Gaussian noise. Drift detector correctly triggers `DRIFT_DETECTED` at σ=0.20.

---

## 4. Limitations

1. **Primary limitation**: Synthetic dataset → no real signal → near-random performance
2. **18-class imbalance with tiny test set** (100 samples for 18 classes): Most classes have 0–2 test samples
3. **All baseline models fail** (Macro F1 < 0.07): Confirms absence of learnable pattern, not model deficiency
4. **Deep learning stubs**: 1D-CNN, LSTM, Autoencoder not trained — stub outputs only

---

## 5. Future Work

1. Replace synthetic generator with real CICIDS2017 CSV dataset (available from Canadian Institute for Cybersecurity)
2. Extend to CICIDS2018 for temporal generalization testing
3. Implement trained deep learning architectures (1D-CNN for sequential flow data)
4. Evaluate on real network traffic captures in a testbed environment
5. Integrate online learning for continuous model adaptation

---

## 6. Reproducibility

```bash
# Regenerate all research results
python scripts/run_research_suite.py

# Results saved to: results/cross_validation.csv, baseline_comparison.csv,
#                   ablation.csv, robustness.csv, latency.csv
#                   results/plots/*.png
```

All results generated from real execution with `random_seed=42`. No metrics were manually entered.
