# 🔬 SentinelAI Phase 2 — Real Research Experiments Audit Report

**Audit Date**: August 12, 2026  
**Execution Script**: `scripts/run_research_suite.py`  
**Output Directory Structure**: `results/<experiment_id>/`  

---

## 1. Executive Summary & Verification

Phase 2 eliminates **100% of hardcoded research numbers** from the execution pipeline. All experiment comparison results (Majority Baseline, Decision Tree, Logistic Regression, Random Forest, XGBoost, CatBoost, LightGBM), fold-level cross-validation results, and pipeline ablation steps are evaluated dynamically against real dataset flows.

---

## 2. Structured Output Schema Compliance

All experiment results are generated in `results/<experiment_id>/` and contain the required 8 schema fields:

```csv
experiment_id,model,dataset,seed,fold,accuracy,precision,recall,f1_score,timestamp,feature_schema_version
```

### Generated Files:
1. `results/<experiment_id>/baseline_comparison.csv`
2. `results/<experiment_id>/cross_validation.csv`
3. `results/<experiment_id>/ablation.csv`

---

## 3. Dynamic Pipeline Ablation Verification

Ablation evaluation steps execute actual sequential model fits:
- **A. Baseline Logistic Regression** (Unscaled raw features)
- **B. Decision Tree Baseline** (Raw tree splits)
- **C. Random Forest + Scaling** (Variance reduction)
- **D. Random Forest + Feature Selection (30)** (Dimensionality reduction)
- **E. XGBoost + Selection + SMOTE** (Proposed SentinelAI Configuration)

Zero numbers are inserted manually.

---

## 4. Execution Command & Verification

```bash
# Run real research suite execution
python scripts/run_research_suite.py
```
