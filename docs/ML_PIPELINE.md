# SentinelAI — ML Pipeline Documentation

**Last Updated**: 2026-08-13

> **Important Honesty Note**: The ML pipeline is architecturally correct and methodologically sound. However, the underlying dataset (`ml/dataset/generator.py`) generates **fully synthetic random data** where features are sampled independently of class labels. There is no meaningful signal for any classifier to learn. Empirical performance is therefore near-random. This limitation is documented here and in MODEL_CARD.md.

---

## 1. Dataset

- **Name**: CICIDS2017 Synthetic Benchmark (Schema-Compatible)
- **Source**: `ml/dataset/generator.py` — synthetic data generator
- **Schema**: Matches CICIDS2017 78-feature flow telemetry schema (`ml/dataset/cicids2017_schema.py`)
- **Sample Count**: 5000 samples (configurable)
- **Classes**: 18 attack classes + BENIGN (see `ATTACK_CLASSES` in `cicids2017_schema.py`)
- **Class Balance**: BENIGN = 70%, each attack class ≈ 1.8%

### Critical Limitation
Features are generated as independent random distributions (Normal, Gamma, Exponential) regardless of class label. **There is no learned signal.** All models perform near-randomly (Macro F1 ≈ 0.04–0.07). This is expected and disclosed.

For realistic performance, the generator must be replaced with actual CICIDS2017 flow data from the Canadian Institute for Cybersecurity.

---

## 2. Train/Test Split

- **Location**: `ml/train_pipeline.py`, function `run_training_pipeline()`
- **Method**: `train_test_split(df, test_size=0.2, stratify=y, random_seed=42)`
- **Order**: Split is performed **before** any preprocessing, SMOTE, or model fitting
- **Guarantee**: Test set is never seen by any preprocessing transformer or model during training

---

## 3. Preprocessing

- **Imputation**: `SimpleImputer(strategy='median')` for numeric columns
- **Scaling**: `StandardScaler` + `RobustScaler` (dual-path in `CICIDS2017Preprocessor`)
- **Infinity handling**: `np.inf` / `-np.inf` replaced with `np.nan` before imputation
- **Non-numeric columns** (`Source IP`, `Destination IP`, `Protocol`) dropped

---

## 4. Feature Selection

- **Method**: `SelectKBest(score_func=f_classif, k=30)` — ANOVA F-statistic top-30 features
- **Leakage prevention**: Feature selector fitted **inside each CV fold** on training fold only; applied (not fitted) on validation fold
- **Final model**: Feature selector fitted on full training set, applied to test set

---

## 5. Class Imbalance — SMOTE

- **Library**: `imbalanced-learn`
- **Method**: `SMOTE(k_neighbors=min(5, min_class_count-1))`
- **Leakage prevention**: SMOTE applied **inside each CV fold** on training fold only; never applied to validation or test folds
- **Adaptive k**: `k_neighbors` dynamically set based on rarest class count to avoid errors on tiny minorities

---

## 6. Cross-Validation

- **Method**: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`
- **Applied to**: Training set only
- **Pipeline per fold** (leakage-free):
  1. Fit `StandardScaler` on `X_train_fold`
  2. Fit `SelectKBest` on `X_train_fold`
  3. Apply SMOTE on `X_train_fold`
  4. Train `RandomForestClassifier(n_estimators=50)` on `X_train_fold`
  5. Transform `X_val_fold` with fold-fitted transformers (no re-fitting)
  6. Evaluate on `X_val_fold`

---

## 7. Model Suite

| Model | Type | CV Macro F1 (Mean) | Notes |
|:---|:---|:---|:---|
| Random Forest | Classical Ensemble | 0.042 ± 0.008 | Champion by selection score |
| XGBoost | Boosting | 0.050 ± 0.009 | |
| LightGBM | Boosting | 0.054 ± 0.012 | |
| CatBoost | Boosting | 0.044 ± 0.009 | |
| Decision Tree | Classical | 0.067 ± 0.021 | Highest F1, highest variance |
| Logistic Regression | Classical | 0.034 ± 0.008 | |
| SVM | Classical | 0.043 ± 0.001 | |
| KNN | Classical | 0.033 ± 0.016 | |
| Naive Bayes | Classical | 0.033 ± 0.024 | |
| 1D-CNN | Deep Learning | stub — returns majority | Not trained |
| LSTM | Deep Learning | stub — returns majority | Not trained |
| Autoencoder | Deep Learning | stub — returns majority | Not trained |

> **Note**: All CV Macro F1 values are near-random because the synthetic dataset has no signal. Values are taken from `ml/artifacts/metadata.json` — the actual execution output.

---

## 8. Model Selection

- **Selection score**: Weighted composite: `0.4×F1 + 0.3×Recall + 0.2×(1−FPR) + 0.1×(1/latency)`
- **Champion**: The model with the highest selection score (Decision Tree in EXP-2026-002 leaderboard)
- **Production model** (`best_model.joblib`): Decision Tree v1.0 (highest selection score: 0.3293)

---

## 9. Final Test Set Evaluation

- **Executed ONCE** after champion selection
- **Never used** for hyperparameter tuning or model selection
- **Metrics** (`metadata.json → final_test_metrics`):
  - Accuracy: 0.16
  - Macro F1: 0.02
  - Precision: 0.0356
  - Recall: 0.0139
  - FPR: 0.0565
  - ROC-AUC: 0.4787

---

## 10. FPR Calculation

$$\text{FPR} = \frac{FP}{FP + TN}$$

For multiclass: one-vs-rest per class, then macro-averaged. Implemented in `ml/metrics/fpr_calculator.py`. Never replaced by `1 - recall`.

---

## 11. Limitations

1. **Synthetic dataset**: No real network traffic signal → near-random performance
2. **18-class imbalance**: Most attack classes have ≤ 2 samples in test set
3. **Feature independence**: Generated features are statistically independent of label — no separability
4. **Small dataset**: 5000 samples for 18-class classification is severely insufficient
5. **Deep learning stubs**: 1D-CNN, LSTM, Autoencoder return stub predictions only
