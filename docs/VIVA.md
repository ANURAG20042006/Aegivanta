# SentinelAI — Viva Q&A Preparation Guide

**IMPORTANT**: All answers in this document reflect the actual implementation. No answer should be changed to impress an examiner if it does not match the code.

---

## Q1: Why this problem?

Network intrusion detection is a high-stakes classification problem. Automated ML-based detection can scale to process thousands of flow records per second where manual rule-writing cannot adapt to novel attack patterns. The project demonstrates how a production MLOps system handles the full lifecycle from training to deployment.

---

## Q2: Why this dataset?

The CICIDS2017 schema was chosen because it is the most widely cited network intrusion detection benchmark in academic literature (hundreds of citations). It provides 78 realistic network flow features (packet counts, byte lengths, inter-arrival times, flag counts) captured from real network traffic.

**However — critical honesty point for the viva**: This project uses a **synthetic generator** (`ml/dataset/generator.py`) that produces random data matching the CICIDS2017 feature schema but without the class-conditional distributions of the real dataset. This was done to avoid distributing the full 2.8 GB dataset. As a result, all classifiers perform near-randomly (~0.04 macro F1). For production use, the generator must be replaced with real CICIDS2017 CSV files.

---

## Q3: Why these features?

78 CICIDS2017 features cover: packet size statistics, inter-arrival time (IAT) distributions, TCP flag counts, flow duration, byte rates, and packet rates. These are computed from network flow records without requiring deep packet inspection (DPI), making them practical for encrypted traffic monitoring.

Feature selection (`SelectKBest`, top 30 by ANOVA F-statistic) is applied inside each CV fold to select the most discriminative subset for the current training partition.

---

## Q4: Why SMOTE?

Many attack classes are extremely rare (< 2% of traffic). Without rebalancing, a classifier can achieve high accuracy by predicting BENIGN for everything. SMOTE generates synthetic minority class samples by interpolating between k nearest neighbors, encouraging the classifier to learn attack-class decision boundaries.

SMOTE is applied **inside each CV fold on the training split only** to prevent information leakage from validation folds into the synthetic samples.

---

## Q5: Why feature selection?

With 78 features and small sample counts, feature selection reduces overfitting risk and improves generalization. SelectKBest with ANOVA F-statistic ranks features by their univariate discriminative power between classes.

---

## Q6: Why these models?

Multiple classical and boosting models were evaluated to provide a comparative baseline:
- **Random Forest**: Robust to outliers, low bias, good generalization
- **XGBoost / LightGBM / CatBoost**: State-of-the-art gradient boosting, often best on tabular data
- **Decision Tree**: Interpretable, fast, but prone to overfitting
- **Logistic Regression**: Linear baseline to measure data separability
- **SVM / KNN / Naive Bayes**: Additional classical baselines

---

## Q7: Why cross-validation?

5-Fold Stratified K-Fold Cross-Validation provides a statistically robust estimate of generalization performance without touching the held-out test set. The model selection decision is made entirely from CV metrics, ensuring the test set remains unseen.

---

## Q8: How did you prevent data leakage?

Three leakage prevention mechanisms:
1. **Split first**: `train_test_split()` called before any preprocessing
2. **Inside-fold preprocessing**: `StandardScaler`, `SelectKBest`, and `SMOTE` are all **fitted inside each fold on the fold's training partition only**, then applied (not re-fitted) on the validation partition
3. **Test isolation**: The final test set is never passed to any preprocessing or model fitting step until after champion selection

Code reference: `ml/train_pipeline.py`, `run_leakage_free_cv()` (lines 39–135)

---

## Q9: Why was test data isolated?

Using test data for model selection or hyperparameter tuning inflates apparent performance (optimistic bias). The test set is the only unbiased estimate of real-world generalization. It is evaluated **exactly once** after the champion model is selected via CV.

---

## Q10: How does model promotion work?

1. Training job triggered via `POST /api/v1/train/trigger` (analyst or admin)
2. Trained model enters `CANDIDATE` state in `ModelRegistry`
3. Admin calls `POST /api/v1/train/promote`
4. Promotion gate checks (fail-closed):
   - Candidate FPR ≤ Champion FPR (missing FPR → rejected)
   - Candidate Recall ≥ Champion Recall (missing → rejected)
   - Candidate latency within threshold (missing → rejected)
   - Per-class FPR regression check
5. On PASS: Candidate → ACTIVE, Champion → ARCHIVED
6. On FAIL: Candidate stays CANDIDATE, reason returned

---

## Q11: How does rollback work?

1. Admin calls `POST /api/v1/train/rollback` with target model ID
2. System verifies SHA256 hash of target model artifact against stored hash in `artifact_manifest.json`
3. On hash mismatch → rejected (corrupt artifact cannot be promoted)
4. On hash match → target model set ACTIVE, current ACTIVE set ARCHIVED
5. Rollback is audit-logged

---

## Q12: How is security enforced?

- **Authentication**: JWT Bearer tokens, HS256, 8-hour expiry. All protected routes use `Depends(get_current_user)`
- **Authorization**: Role-based via `Depends(require_role("admin"))` — promotion and rollback require admin
- **Secrets**: In PRODUCTION mode, `validate_production_settings()` raises RuntimeError if `SECRET_KEY`, `POSTGRES_PASSWORD`, or any user password is missing
- **CORS**: Wildcard `*` and localhost origins rejected in PRODUCTION mode
- **Audit log**: Every mutation written to `AuditLog` table via request middleware

---

## Q13: How does SHAP work?

SHAP (SHapley Additive exPlanations) uses cooperative game theory. For each prediction:
- Each feature's contribution is calculated as the average marginal change in model output when the feature is added across all possible feature subsets
- For tree models, `TreeExplainer` computes exact SHAP values in `O(TLD²)` time (T=trees, L=leaves, D=depth)
- Output: Feature attribution dict with `feature`, `contribution` (SHAP value), `input_value`, `rank`, `direction` (positive/negative)

Implementation: `ml/explainability/real_explainer.py`

If the model does not support SHAP, returns `{"available": false, "reason": "..."}` — never fabricated.

---

## Q14: How is drift detected?

`AccumulatedWindowDriftDetector` (`ml/monitoring/drift_detector.py`):
1. Accumulates predictions into a sliding window (minimum 50 samples before evaluating)
2. **PSI (Population Stability Index)**: Compares current prediction distribution vs. baseline using 10-bin histogram. PSI > 0.25 → DRIFT_DETECTED
3. **KS Test**: `scipy.stats.ks_2samp` compares feature distributions between baseline and window. p-value < 0.01 → drift flagged
4. Baseline distribution stored with SHA256 hash to detect baseline tampering
5. Emits `retraining_recommended=True` on drift — does NOT automatically promote a new model

---

## Q15: Why could performance be poor?

**The actual measured performance is poor**: CV Macro F1 ≈ 0.04–0.07. This is because:
1. The synthetic dataset generator creates features as independent random distributions regardless of class label
2. No classifier can learn meaningful patterns from random noise
3. With 18 classes and equal feature distributions per class, random guessing achieves ~1/18 ≈ 0.056 F1

This is an honest limitation, not a system bug. The MLOps pipeline, preprocessing, leakage prevention, and security architecture are all correct.

---

## Q16: What are the limitations?

1. **Synthetic dataset with no signal** — core limitation
2. **18-class extreme imbalance** — rare classes have < 5 test samples
3. **Small dataset** — 5000 samples insufficient for 18-class deep learning
4. **Deep learning stubs** — 1D-CNN, LSTM, Autoencoder are placeholder stubs
5. **SQLite in development** — not suitable for high-concurrency production
6. **No TLS/HTTPS** — requires reverse proxy (nginx + certbot) for production HTTPS

---

## Q17: What would production deployment require?

1. Real CICIDS2017 dataset (replace `ml/dataset/generator.py` with CSV loader)
2. Retrain pipeline on real data to get meaningful model performance
3. PostgreSQL in production (set `DATABASE_URL`, `POSTGRES_PASSWORD`)
4. HTTPS via nginx reverse proxy + TLS certificate (Let's Encrypt)
5. Set `OPERATING_MODE=PRODUCTION` with all required secrets
6. Deploy ML artifacts volume to persistent storage
7. Configure monitoring alerting (Prometheus / Grafana) on drift endpoints
8. Periodic retraining schedule triggered by drift detector recommendations
