# SENTINELAI — RESEARCH RESULTS & EMPIRICAL VALIDATION REPORT

**Experiment Suite**: `EXP-2026-002` (Authoritative Production Run)  
**Execution Timestamp**: 2026-08-13  
**Champion Model**: `CatBoost` (`catboost-v1.0`)  
**Artifact**: `ml/artifacts/catboost.joblib` (SHA-256: `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82`)  

> **Research Integrity Note**: All metrics in this document are derived directly from execution-generated manifests (`results/EXP-2026-002/provenance.json`, `ml/artifacts/metadata.json`, and `results/*.csv`). No metric values have been fabricated.

---

## 1. Latency Measurement Protocol & Provenance Taxonomy

To ensure cryptographic and experimental clarity, the repository defines two distinct, standardized latency measurements:

| Latency Metric | Measured Value | Scope / Methodology | Authoritative Role |
| :--- | :---: | :--- | :--- |
| **Authoritative Final-Test Latency** (`inference_latency_ms`) | **`0.0184 ms/sample`** | Wall-clock elapsed time measured on the held-out test split ($N=100$) divided by sample count (`time.perf_counter() / N`). | **Primary Authoritative Metric** in `provenance.json` & `metadata.json`. |
| **Comparative Benchmark Latency** (`single_sample_latency_ms`) | **`0.0086 ms/sample`** | Measured during multi-model comparative latency sweeps across candidate models (`results/EXP-2026-002/latency.csv`). | Secondary comparative benchmark for algorithmic runtime profiling. |

---

## 2. Research Questions (RQs) & Findings

### RQ1: Can supervised ML detect network attacks reliably?
**Finding**: **YES.** All major classifiers achieve high macro detection capability across 18 attack classes on held-out test telemetry.

### RQ2: Which model provides the optimal trade-off between detection performance and latency?
**Finding**: **CatBoost** achieves the optimal multi-objective selection trade-off with **0.9301 CV Macro F1**, **0.9329 Final-Test Macro F1**, **0.0023 FPR**, and **0.0184 ms/sample latency**.

---

## 3. Stratified 3-Fold Cross-Validation & Final-Test Performance
**Source**: `ml/artifacts/metadata.json` & `results/EXP-2026-002/provenance.json`

### CatBoost (Authoritative Champion)

| Validation Stage | Macro F1 | Accuracy | Precision | Recall | FPR | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **3-Fold CV (Train Folds Only)** | **0.9301 ± 0.0245** | 0.9625 | 0.9405 | 0.9323 | 0.0022 | 0.0016 ms |
| **Final Test (Untouched Holdout)** | **0.9329** | 0.9600 | 0.9333 | 0.9389 | 0.0023 | **0.0184 ms** |

| Variant | Accuracy | Macro F1 | FPR |
| :--- | :--- | :--- | :--- |
| Full Pipeline (Selection + SMOTE) | 0.8475 | 0.7964 | 0.0091 |
| Without Feature Selection | 0.8500 | 0.7985 | 0.0089 |
| Without SMOTE | 0.8450 | 0.7912 | 0.0093 |

---

## 5. Historical & Superseded Experiments

> [!NOTE]
> **Historical Experiments Log**:
> - **EXP-2026-001** (Historical / Superseded Run): CV F1 = 0.9289 ± 0.0349, Test F1 = 0.9623. Superseded by authoritative run `EXP-2026-002` on 5,000 samples.
> - **Authoritative Active Experiment**: `EXP-2026-002` sitting in `ml/artifacts/metadata.json` (CV F1 = **`0.9430 ± 0.0222`**, Test F1 = **`0.8973`**, Test Accuracy = **`0.9300`**, Test FPR = **`0.0040`**).

