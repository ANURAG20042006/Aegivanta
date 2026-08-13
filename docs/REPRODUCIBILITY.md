# SentinelAI — Dependency Reproducibility & Clean-Environment Guide

**Version**: 1.0.0  
**Experiment**: `EXP-2026-002`  
**Python**: 3.11.5  
**Last verified**: 2026-08-13  
**Verified result**: 132 passed, 1 skipped, 0 failures (pytest -q, 199.62s)

> [!IMPORTANT]
> **Precision of reproducibility claim**: Environment reproducibility is enforced through
> pinned artifact-critical dependencies and a recorded dependency resolution.
> Bit-for-bit numerical reproducibility on floating-point results is NOT guaranteed
> across different operating systems or hardware. Results have been verified to match
> on Python 3.11.5 / Windows 10 with the dependency versions listed below.

---

## 1. Dependency Source of Truth

| File | Role | When to use |
|:---|:---|:---|
| [`requirements.txt`](../requirements.txt) | **Authoritative install spec** | Normal development & CI install |
| [`requirements-lock.txt`](../requirements-lock.txt) | Full resolved pip freeze | Exact reproduction of tested environment |
| [`backend/requirements.txt`](../backend/requirements.txt) | Backend alias | References root `requirements.txt` via `-r ../requirements.txt` |

**`requirements.txt` is the single source of truth.**  
`backend/requirements.txt` is a one-line redirect and introduces no additional packages.

> [!CAUTION]
> Never install dependencies from any other source (e.g., `pip install pytest numpy ...`).
> Always use `pip install -r requirements.txt`.

---

## 2. Critical ML Package Versions

### Artifact-Critical (EXACT version required)

These packages were used to serialize the ML artifacts (`best_model.joblib`, `preprocessor.joblib`).  
Loading artifacts under a **different version will produce an `InconsistentVersionWarning` or incorrect results**.

| Package | Required Version | Purpose |
|:---|:---:|:---|
| `scikit-learn` | **1.6.1** | Model training, preprocessing pipeline, cross-validation |
| `numpy` | **2.2.2** | Numerical arrays — artifact data representation |
| `pandas` | **2.2.3** | DataFrame operations — feature alignment |

### Bounded-Compatible (range-checked)

These packages do not directly serialize into artifacts but must remain within the tested range
to avoid API breakage or numerical divergence.

| Package | Tested Version | Supported Range |
|:---|:---:|:---|
| `scipy` | 1.15.2 | `>=1.15.0, <2.0.0` |
| `joblib` | 1.4.2 | `>=1.4.0, <2.0.0` |
| `xgboost` | 3.0.1 | `>=3.0.0, <4.0.0` |
| `lightgbm` | 4.7.0 | `>=4.0.0, <5.0.0` |
| `catboost` | 1.2.8 | `>=1.2.0, <2.0.0` |
| `shap` | 0.51.0 | `>=0.51.0, <1.0.0` |
| `imbalanced-learn` | 0.14.2 | `>=0.14.0, <1.0.0` |

---

## 3. Artifact Compatibility Record

| Artifact | Type | Feature dimension | SHA-256 (prefix) |
|:---|:---|:---:|:---|
| `ml/artifacts/best_model.joblib` | GaussianNB | 30 features | `5a01833d72ed2ec5` |
| `ml/artifacts/preprocessor.joblib` | CICIDS2017Preprocessor | 30 features | `e5c07b23b9a82ca2` |
| `ml/artifacts/metadata.json` | Experiment metadata | `EXP-2026-002` | — |

**Artifact generation context**:
- Python: `3.11.5`
- scikit-learn: `1.6.1`
- numpy: `2.2.2`
- pandas: `2.2.3`
- Training timestamp: `2026-08-13T13:01:52 UTC`
- Random seed: `42`
- Dataset hash: `62aa92a7d54fe464`
- Git commit: `9d34be31d17b59036d7d1fedee50ff3f690c7a52`

---

## 4. Experiment Identification

| Parameter | Value |
|:---|:---|
| **Experiment ID** | `EXP-2026-002` |
| **Random seed** | `42` |
| **Dataset** | `synthetic_cicids2017_benchmark` |
| **Dataset hash** | `62aa92a7d54fe464` |
| **Selected model** | `GaussianNB` (Naive Bayes) |
| **Feature schema** | `schema-v1.0` (30 features) |
| **Feature schema version** | `schema-v1.0` |
| **CV F1 (macro, mean)** | `0.9289` (std: `0.0349`) |
| **Test F1 (macro)** | `0.9623` |
| **Test Accuracy** | `0.98` |
| **Test FPR** | `0.0012` |
| **Test ROC-AUC** | `0.9996` |

---

## 5. Clean Environment Setup

```bash
# Step 1 — Clone
git clone https://github.com/ANURAG20042006/SENTINELAI.git
cd SENTINELAI

# Step 2 — Create virtual environment
python -m venv .venv

# Step 3 — Activate
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Step 4 — Install dependencies (authoritative source)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Step 5 — Configure environment variables
cp .env.example .env
# Edit .env and fill in SENTINEL_ADMIN_PASSWORD, SECRET_KEY, etc.
```

> [!TIP]
> For the exact resolved environment (every transitive dependency pinned),
> use `requirements-lock.txt` instead:
> ```bash
> pip install -r requirements-lock.txt
> ```

---

## 6. Verification Command Suite

```bash
# Environment verification (artifact-critical versions + bounded checks)
python scripts/verify_environment.py
# Expected: ALL REQUIRED DEPENDENCIES VERIFIED OK

# Python syntax check
python -m compileall -q backend ml scripts tests
# Expected: exit code 0, no errors

# Full test suite
python -m pytest -q
# Expected: 132 passed, 1 skipped, 0 failures

# Artifact integrity check
python scripts/verify_release.py
# Expected: ALL RELEASE VERIFICATION STAGES PASSED

# Full integrity audit
python scripts/final_integrity_audit.py
# Expected: ALL CRITICAL CHECKS PASSED
```

---

## 7. Recreating the ML Artifacts

> [!WARNING]
> Do NOT regenerate artifacts unless the current artifacts are corrupted or
> a dependency change makes them incompatible. Regenerating may produce
> numerically different (but statistically equivalent) results due to
> pseudo-random variation, which would require updating `metadata.json`.

If regeneration is required:
```bash
# Ensure the exact artifact environment is active
python -m ml.train_pipeline
# Verify the new artifacts pass all checks
python scripts/verify_release.py
```

---

## 8. Frontend Reproduction

```bash
cd frontend
npm ci             # Install exact versions from package-lock.json
npm run build      # Production build → dist/index.html
```

Node.js version tested: `20.x`

---

## 9. Git Reference

- **Repository**: https://github.com/ANURAG20042006/SENTINELAI
- **Authoritative branch**: `master`
- **Artifact generation commit**: `9d34be31d17b59036d7d1fedee50ff3f690c7a52`
