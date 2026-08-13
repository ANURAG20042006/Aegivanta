# SentinelAI — Phase 11 Initial Baseline Audit Document

**Audit Timestamp**: 2026-08-13 (Phase 11 Audit Initial State)  
**Auditor**: Antigravity AI Pair Programmer  

---

## 1. System Environment & Source State
- **Python Version**: `3.11.5 (tags/v3.11.5:cce6ba9)`
- **Node / npm Version**: `Node v23.1.0` / `npm 10.9.0`
- **Git Commit Hash**: `1948f5a7e45dff4dddabc51ebfb621f40e799beb`
- **Dataset Identifier**: `synthetic_cicids2017_benchmark`
- **Dataset Hash**: `2acdcd9c8cb49635`

---

## 2. Artifact & Dimension Mismatch Baseline
- **`preprocessor.joblib` Output Feature Count**: `30` features selected.
- **`best_model.joblib` Input Dimension (`n_features_in_`)**: `78` features expected (DecisionTreeClassifier).
- **Status**: 🔴 **CRITICAL DIMENSION MISMATCH** (`30` vs `78`). High-priority architectural resolution required in Phase 1.

---

## 3. Test & Build Verification Baseline
- **Pytest Output**: `61 passed` in 176.03s (using `python -m pytest -q`).
- **Frontend Build Output**: `npm run build` succeeded (`tsc && vite build` built in 5.92s).
- **Research Suite Output**: Completed all 7 benchmark phases.

---

## 4. Code Integrity & Fallback Baseline Findings
- **Hardcoded Credentials**:
  - `docker/docker-compose.yml`: Default password fallback `${POSTGRES_PASSWORD:-<CONFIGURED_DB_PASSWORD>}`.
  - `backend/app/config.py`: Hardcoded fallback defaults for database credentials.
- **Hardcoded Probabilities & Confidence**:
  - `ml/models/deep_learning.py`: Hardcoded `probs[i, 1] = 0.95` and `probs[i, 0] = 0.95` for Autoencoder anomaly scores.
  - `ml/explainability/real_explainer.py`: Hardcoded fallback `confidence: float = 0.95`.
- **Hardcoded Metric Fallbacks**:
  - `ml/train_pipeline.py`: Hardcoded `"macro_f1_std": 0.001`.
- **FPR Calculation Methodology**:
  - `ml/models/model_selector.py`: `fpr = float(1.0 - rec)` (Mathematically incorrect: FNR calculated instead of FPR = FP / (FP + TN)).
- **ROC Data Implementation**:
  - Dynamic ROC points generated on test set, but historical baselines require explicit decoupled reference file binding (`research/reference/historical_benchmarks.json`).
