# SentinelAI Research Integrity Audit Report

**Audit Date**: August 12, 2026
**Auditor**: Automated forensic inspection + manual review

---

## Audit Checklist

| # | Requirement | Status | Evidence |
|:-:|:------------|:------:|:---------|
| R1 | Test set frozen after TRAIN/TEST split - never seen by preprocessor fit, SMOTE, or feature selection | **PASS** | TestSetFrozenProof (2/2 pass) |
| R2 | Champion selected via CV on TRAIN only - NOT on test F1 | **PASS** | train_and_select_champion() has no X_test/y_test; TestChampionSelectionNotOnTestData (2/2 pass) |
| R3 | Ablation variants are fully independent pipelines - NO arithmetic derivation | **PASS** | Variants A/B/C each independently call CICIDS2017Preprocessor().fit_transform_train_test() + RF.fit() |
| R4 | metadata.json has training_metrics, cv_metrics, validation_metrics, final_test_metrics | **PASS** | Verified live; TestMetadataJsonStructure (1/1 pass) |
| R5 | No fabricated confidence fallbacks - predict_proba() used, None if unavailable | **PASS** | real_confidence = float(np.max(proba)); TestNoFabricatedConfidence (1/1 pass) |
| R6 | No fabricated ablation arithmetic (metric - 0.008, metric - 0.025) | **PASS** | Old patterns deleted; ablation.csv now has real empirical values |
| R7 | README / docs hardcoded accuracy claims removed | **PASS** | README.md, VIVA.md, VIVA_PRESENTATION_GUIDE.md, PROJECT_EVALUATION_REPORT.md, Dashboard.tsx cleaned |
| R8 | CICIDS2017Preprocessor(n_features_to_select=None) works correctly | **PASS** | preprocessor.py - actual_k = "all" if None else min(k, n_cols) |
| R9 | python -m compileall backend ml scripts -q clean | **PASS** | Exit code 0 |
| R10 | Integrity tests: test_research_integrity.py + test_leakage_proof.py | **PASS** | 11/11 pass |

---

## Issues Found and Fixed

### 1. Fabricated Ablation Arithmetic (FIXED)

Location: scripts/run_research_suite.py (old Variants B and C)

OLD - FABRICATED: no training occurred, values derived arithmetically:
  "accuracy": round(accuracy_score(y_test, y_pred_full) - 0.008, 4),  # Variant B
  "accuracy": round(accuracy_score(y_test, y_pred_full) - 0.025, 4),  # Variant C

NEW - REAL: independent preprocessor + model training per variant:
  preproc_b = CICIDS2017Preprocessor(n_features_to_select=None)
  X_tr_b, X_te_b, y_tr_b, y_te_b = preproc_b.fit_transform_train_test(df, ...)
  rf_b = RandomForestClassifier(n_estimators=50, random_state=seed)
  rf_b.fit(X_tr_b, y_tr_b)

### 2. Fabricated Confidence Fallback (FIXED)

Location: Old run_research_suite.py XAI section
Problem: confidence=0.9850 -- hardcoded float
Fix:
  proba = rf_champion.predict_proba(sample_vector)
  real_confidence = float(np.max(proba)) if proba is not None else None
  xai_output["confidence_source"] = "predict_proba"

### 3. Hardcoded Accuracy in Docs and UI (FIXED)

Locations: README.md, VIVA.md, VIVA_PRESENTATION_GUIDE.md, PROJECT_EVALUATION_REPORT.md, Dashboard.tsx
All hardcoded figures (99.12%, 98.85%, 98.95%, 98.60%) replaced with references to results/EXP-2026-001/research_summary.json

### 4. Preprocessor None Crash (FIXED)

Location: ml/dataset/preprocessor.py line 95
Problem: min(None, X_train_raw.shape[1]) raises TypeError
Fix:
  if self.n_features_to_select is None:
      actual_k = "all"
  else:
      actual_k = min(self.n_features_to_select, X_train_raw.shape[1])

---

## Champion Selection Proof (Live Run)

  === Champion Model Selected: SVM (Selection Score: 0.9783) ===
  Sections in metadata.json: [..., training_metrics, cv_metrics, validation_metrics, final_test_metrics, ...]

The live champion is SVM - not the prototype-era "XGBoost 99.12%" claim.
Selection used CV composite score (F1x0.40 + Recallx0.30 + (1-FPR)x0.20 + Latencyx0.10) on TRAIN data only.

---

## Test Suite Results

  python -m pytest -v tests/ml/test_research_integrity.py tests/ml/test_leakage_proof.py
  => 11 passed

  python -m compileall backend ml scripts -q
  => exit code 0

  python scripts/run_research_suite.py
  => --> 4. Executing Real Independent Pipeline Ablation Study...
  => [SUCCESS] Research Suite Completed. Outputs in: results/EXP-2026-001/

---

## Remaining Academic Context Items

| File | Content | Status |
|:-----|:--------|:-------|
| docs/PROJECT_REPORT.md | "0.9901 macro F1-score, 99.12% accuracy" | Retained for doc continuity -- labelled prototype era |
| docs/PROJECT_EVALUATION_REPORT.md | 12-model leaderboard | Accuracy columns removed; IMPORTANT caveat + pointer to results/EXP-2026-001/ added |
| docs/VIVA_PRESENTATION_GUIDE.md | Model accuracy table | Accuracy columns removed; NOTE caveat + pointer to results/EXP-2026-001/ added |

NOTE: docs/PROJECT_REPORT.md retains the original abstract text.
Examiners must be directed to results/EXP-2026-001/research_summary.json for reproducible current results.
