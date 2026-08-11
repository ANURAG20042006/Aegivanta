# 🛡️ SentinelAI Phase 1 — Leakage-Free ML Pipeline Verification Document

**Audit Date**: August 12, 2026  
**Pipeline Version**: `split_first_smote_inside_folds_only`  
**Feature Schema Contract Version**: `schema-v1.0`  

---

## 1. Executive Summary & Verification

Phase 1 guarantees **100% data-leakage elimination** across training, cross-validation, feature selection, and test set evaluation. No preprocessing operations (`StandardScaler`, `SelectKBest`, `SMOTE`) fit on test or validation splits.

---

## 2. Requirement Compliance Matrix

| Requirement | Implementation Architecture | Evidence & Code Location |
| :--- | :--- | :--- |
| **REQ 1: Final Test Split** | `train_test_split(test_size=0.20, stratify=y)` performed FIRST. `(X_test, y_test)` is frozen and untouched throughout preprocessor fitting, SMOTE, CV, and model selection. | [`ml/dataset/preprocessor.py:L86-L90`](file:///c:/Users/NJ542WS/Desktop/major%20project/ml/dataset/preprocessor.py#L86-L90) |
| **REQ 2: Leakage-Free CV** | `StratifiedKFold(n_splits=5)` fits `StandardScaler`, `SelectKBest`, and `SMOTE` strictly inside `X_train_fold`. `X_val_fold` is transformed using fitted fold transformers ONLY. | [`ml/train_pipeline.py:L40-L100`](file:///c:/Users/NJ542WS/Desktop/major%20project/ml/train_pipeline.py#L40-L100) |
| **REQ 3: Hyperparameter Search** | Parameter optimization operates strictly on `X_train`. `X_test` remains completely invisible. | [`ml/train_pipeline.py:L115-L130`](file:///c:/Users/NJ542WS/Desktop/major%20project/ml/train_pipeline.py#L115-L130) |
| **REQ 4: Final Training** | After candidate selection, configuration is frozen. Preprocessor is fitted on `X_train`, SMOTE is applied to `X_train`, and `X_test` is evaluated ONCE. | [`ml/train_pipeline.py:L135-L150`](file:///c:/Users/NJ542WS/Desktop/major%20project/ml/train_pipeline.py#L135-L150) |
| **REQ 5: Reproducibility Metadata** | Serializes `metadata.json` containing `dataset_identifier`, `dataset_hash`, `train_test_split`, `random_seed`, `selected_features`, `cv_metrics`, `leaderboard`, `preprocessing_version`, `git_commit`. | [`ml/artifacts/metadata.json`](file:///c:/Users/NJ542WS/Desktop/major%20project/ml/artifacts/metadata.json) |

---

## 3. Automated Test Suite Proof (`tests/pytest/test_leakage_proof.py`)

- `test_test_data_never_reaches_smote`: Proves `X_test` size matches exact split fraction and is not oversampled.
- `test_preprocessing_not_fitted_on_test_data`: Proves `scaler.mean_` matches manual scaler fitted strictly on `X_train`.
- `test_cv_folds_independently_fit_preprocessing`: Proves every CV fold fits independent transformer instances.
- `test_final_test_evaluated_only_after_model_selection`: Proves single final evaluation on test set.

```bash
# Execution verification
python -m pytest tests/pytest/test_leakage_proof.py -v
```
