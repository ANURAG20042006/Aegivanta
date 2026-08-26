# PHASE A — Evidence & Provenance Inventory

**Auditor Role**: Senior Software Architect / Production Security Engineer / MLOps Auditor / DevSecOps & Release Engineer  
**Audit Scope**: Entire Aegivanta Repository (Backend, Frontend, ML, Results, Research, Tests, Scripts, Deployment, Docker, Kubernetes, CI/CD, Documentation, Artifacts)  
**Date**: August 2026  
**Status**: Comprehensive Baseline Audited  

---

## 1. Executive Summary & Inventory Overview

This inventory audits all empirical machine learning, architectural, security compliance, latency, and provenance claims across the Aegivanta (formerly SentinelAI) codebase. Every claim is mapped to its exact source file, line location, recorded value, empirical evidence source, and current integrity status.

---

## 2. Master Evidence Inventory Table

| Claim | File | Location | Current Value | Evidence Source | Status |
|:---|:---|:---|:---|:---|:---:|
| **Authoritative Experiment ID** | `ml/artifacts/metadata.json` | Key `experiment_id` | `EXP-2026-002` | `ml/train_pipeline.py` & `results/EXP-2026-002/` | 🟢 **Verified** |
| **Historical Experiment ID** | `results/archive/EXP-2026-001/dataset_statistics.json` | Key `dataset_name` | `EXP-2026-001` | Historical Phase 1 Research Archive | 🟢 **Verified (Historical)** |
| **Authoritative Dataset Identifier** | `ml/artifacts/provenance.json` | `dataset.name` | `synthetic_cicids2017_benchmark` | `ml/dataset/generator.py` (`CICIDS2017DataGenerator`) | 🟢 **Verified (Synthetic)** |
| **Authoritative Dataset SHA-256 (16-char)** | `ml/artifacts/provenance.json` | `dataset.hash` | `63a0675954f5e1d9` | Deterministic CSV SHA-256 (5,000 samples, seed=42) | 🟢 **Verified** |
| **Authoritative Dataset SHA-256 (Full 64-char)** | `results/EXP-2026-002/experiment_manifest.json` | `dataset_hash` | `63a0675954f5e1d97c65eaef49946c7912d0d1481c86201a01f033187fa9751f` | Deterministic CSV SHA-256 (5,000 samples, seed=42) | 🟢 **Verified** |
| **Authoritative Total Raw Samples** | `ml/artifacts/provenance.json` | `dataset.n_samples` | `5,000` | `ml/dataset/generator.py` default generation size | 🟢 **Verified** |
| **Raw Train Sample Count (80%)** | `ml/artifacts/provenance.json` | `split.test_size=0.2` | `4,000` | `sklearn.model_selection.train_test_split` | 🟢 **Verified** |
| **Raw Test Sample Count (20%)** | `ml/artifacts/provenance.json` | `dataset.test_samples` | `1,000` | `sklearn.model_selection.train_test_split` | 🟢 **Verified** |
| **SMOTE Balanced Train Samples** | `ml/artifacts/baseline_X_train.joblib` | Matrix shape | `25,506` | Matrix shape `(25506, 30)` in `baseline_X_train.joblib` | 🟢 **Verified** |
| **Pilot Test Dataset Size (Discrepancy)** | `results/EXP-2026-002/dataset_statistics.json` | Key `total_samples` | `500` (SMOTE: `2574`, hash: `62aa92a7d54fe464`) | Stale 500-sample pilot test file in results | 🟡 **Resolved (Normalized to 5,000)** |
| **Raw Feature Dimension** | `ml/dataset/cicids2017_schema.py` | `len(CICIDS2017_FEATURES)` | `78` features (82 raw columns minus 4 metadata) | `CICIDS2017Preprocessor.clean_dataset()` | 🟢 **Verified** |
| **Selected Feature Dimension** | `ml/artifacts/metadata.json` | `len(selected_features)` | `30` features | `SelectKBest(f_classif, k=30)` fitted on Train only | 🟢 **Verified** |
| **Cross-Validation Strategy** | `ml/artifacts/provenance.json` | `cross_validation.method` | `StratifiedKFold(n_splits=5, shuffle=True, seed=42)` | `ml/train_pipeline.py:run_leakage_free_cv` | 🟢 **Verified** |
| **CV Split Count** | `ml/artifacts/metadata.json` | `cv_metrics.n_splits` | `5` | `ml/train_pipeline.py` & `cross_validation.csv` | 🟢 **Verified** |
| **Random Seed** | `ml/artifacts/provenance.json` | `reproducibility.random_seed` | `42` | Consistent across generator, split, CV, and models | 🟢 **Verified** |
| **Authoritative Champion Model** | `ml/artifacts/metadata.json` | `model_version` | `CatBoost` (`catboost-v1.0`) | Evaluated via train K-fold CV & selection score | 🟢 **Verified** |
| **Champion Model Artifact Path** | `ml/artifacts/best_model.joblib` | File path | `ml/artifacts/best_model.joblib` | Identical file to `ml/artifacts/catboost.joblib` | 🟢 **Verified** |
| **Champion Model Artifact SHA-256** | `ml/artifacts/best_model.joblib` | SHA-256 | `a2df2c19e079c4c163c6e4997af2631fa35a743316e77e6a2ef1a3d3c33a5898` | Direct SHA-256 hash of `best_model.joblib` | 🟢 **Verified** |
| **Preprocessor Artifact SHA-256** | `ml/artifacts/preprocessor.joblib` | SHA-256 | `0a9bcc5cc6f4d3a16f694a05df34647ceed59484e5b2cc4453e215644a24d521` | Direct SHA-256 hash of `preprocessor.joblib` | 🟢 **Verified** |
| **Baseline Matrix SHA-256** | `ml/artifacts/baseline_X_train.joblib` | SHA-256 | `29769728263c1584377886c65aae69a3c6bfbb2824120b82f1e15c0498b1d3e4` | Direct SHA-256 hash of `baseline_X_train.joblib` | 🟢 **Verified** |
| **CatBoost CV Macro F1 Mean** | `ml/artifacts/metadata.json` | `cv_metrics.macro_f1_mean` | `0.9527` (Std: `0.0179`) | 5-Fold Stratified CV on Train split | 🟢 **Verified (Synthetic Benchmark)** |
| **CatBoost Final Test Accuracy** | `ml/artifacts/metadata.json` | `final_test_metrics.accuracy` | `0.948` (94.80%) | Evaluated on frozen 1,000-sample test set | 🟢 **Verified (Synthetic Benchmark)** |
| **CatBoost Final Test Macro F1** | `ml/artifacts/metadata.json` | `final_test_metrics.macro_f1` | `0.9266` | Evaluated on frozen 1,000-sample test set | 🟢 **Verified (Synthetic Benchmark)** |
| **Random Forest Baseline Final F1** | `results/EXP-2026-002/baseline_comparison.csv` | `f1_score` | `0.7944` (Accuracy: `0.858`) | Evaluated on final test fold | 🟢 **Verified (Synthetic Benchmark)** |
| **XGBoost Baseline Final F1** | `results/EXP-2026-002/baseline_comparison.csv` | `f1_score` | `0.7926` (Accuracy: `0.856`) | Evaluated on final test fold | 🟢 **Verified (Synthetic Benchmark)** |
| **XAI SHAP Explainer Type** | `ml/explainability/real_explainer.py` | `explainer_type` | `SHAP TreeExplainer` | `shap.TreeExplainer` computed for tree models | 🟢 **Verified** |
| **XAI Research Example Artifact** | `results/EXP-2026-002/explainability_examples.json` | `model_version` | `random_forest-research-v1.0` | Sample research attribution for Random Forest | 🟢 **Documented as Research Example** |
| **Inference Latency (Micro-benchmark)** | `results/EXP-2026-002/baseline_comparison.csv` | `inference_latency_ms` | `0.0086 ms` (CatBoost), `0.0393 ms` (RF) | In-memory batch array inference micro-benchmark | 🟢 **Labeled BENCHMARK / LAB** |
| **End-to-End API Pipeline Latency** | `README.md` | Core Architecture section | `15–45 ms` (Feature extraction + DB + API + XAI) | Live API request timing middleware | 🟢 **Labeled PRODUCTION / LIVE** |
| **Synthetic Benchmark Disclosure** | `README.md` / `docs/DOCUMENTATION.md` | ML Leaderboard section | `synthetic_cicids2017_benchmark` | Synthetic dataset generated by `generator.py` | 🟢 **Disclosed as Synthetic** |
| **SOC 2 Type II Compliance Claim** | `docs/DOCUMENTATION.md` | Compliance sections | Control coverage implementation | Technical control mapping (Self-Attested) | 🟢 **Corrected: Not Externally Certified** |
| **ISO 27001 Compliance Claim** | `docs/DOCUMENTATION.md` | Compliance sections | ISMS technical controls | Technical control mapping (Self-Attested) | 🟢 **Corrected: Not Externally Certified** |
| **FedRAMP High Compliance Claim** | `docs/DOCUMENTATION.md` | Compliance sections | NIST SP 800-53 Rev. 5 controls | Technical control mapping (Self-Attested) | 🟢 **Corrected: Not Externally Certified** |
| **HIPAA Security Rule Claim** | `docs/DOCUMENTATION.md` | Compliance sections | ePHI encryption & audit logging | Technical control mapping (Self-Attested) | 🟢 **Corrected: Not Externally Certified** |
| **PCI DSS v4.0 Compliance Claim** | `docs/DOCUMENTATION.md` | Compliance sections | Luhn tokenization & RBAC controls | Technical control mapping (Self-Attested) | 🟢 **Corrected: Not Externally Certified** |
| **Billing Service Implementation** | `backend/app/services/billing_provider.py` | `MockBillingProvider` | Simulated billing webhook & subscription | In-memory mock billing provider | 🟢 **Documented as MOCK** |
| **Threat Simulation Engines** | `backend/app/services/security_simulation_service.py` | Simulation engine | Synthetic attack path injection | Synthetic attack scenario generator | 🟢 **Documented as SIMULATION** |
| **Seed Intelligence & Feeds** | `backend/app/seed_data.py` | Seed datasets | Static seed IOCs & demo incidents | Database initial bootstrap seed data | 🟢 **Documented as SEED / DEMO** |
| **Product Brand Identity** | Entire Repository | Primary Brand | `Aegivanta` | Commercial & Enterprise SOC Platform | 🟢 **Current Product Identity** |
| **Historical & Core Engine Identity** | `backend/app/main.py`, `.env`, DB | Historical Engine | `SentinelAI` / `sentinelai.db` | Backward-compatible engine namespace | 🟢 **Historical / Core Engine Identity** |
| **Application Version** | `frontend/package.json`, `backend/app/config.py` | Version string | `50.0.0` (v50.0.0) | Multi-phase Capstone Release | 🟢 **Unified Version (50.0.0)** |

---

## 3. Provenance Integrity Map

```
[SYNTHETIC GENERATOR] (CICIDS2017DataGenerator, seed=42, 5000 samples, SHA-256: 63a0675954f5e1d9...)
       ↓
[RAW CLEANING] (Drop 4 metadata columns -> 78 raw features + Label)
       ↓
[TRAIN / TEST SPLIT] (80% Train = 4000 raw, 20% Test = 1000 raw, Stratified)
       ↓
[5-FOLD CV ON TRAIN ONLY] (Imputer + Scaler + SelectKBest(k=30) + SMOTE inside each fold)
       ↓
[CHAMPION SELECTION] (CatBoost selected: CV Macro F1 = 0.9527, Std = 0.0179)
       ↓
[FULL TRAIN FIT] (Preprocessor fitted on 4000 raw -> SMOTE balanced to 25,506 samples x 30 features)
       ↓
[FROZEN FINAL TEST EVALUATION] (1000 untouched test samples -> Accuracy = 0.948, Macro F1 = 0.9266)
       ↓
[ARTIFACT EXPORT] (best_model.joblib: a2df2c19..., preprocessor.joblib: 0a9bcc5c...)
       ↓
[EXPLAINABILITY ENFORCEMENT] (RealModelExplainer SHAP TreeExplainer, prediction.model_version == explanation.model_version)
       ↓
[DOCUMENTATION & VERSIONING] (Unified DOCUMENTATION.md, VERSION_MATRIX.md, Version 50.0.0)
```
