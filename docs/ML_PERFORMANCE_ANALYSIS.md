# SentinelAI Empirical Machine Learning Performance & System Analysis

**Experiment Reference**: EXP-2026-002  
**Dataset Identifier**: `synthetic_cicids2017_benchmark` (5,000 samples, 78 raw features, 18 target attack classes)  
**Methodological Protocol**: Decoupled split-first architecture with fold-local scaling, SelectKBest feature selection, and fold-local SMOTE. Single evaluation on frozen untouched test set.

---

## 1. Class Distribution & Benchmark Overview
The benchmark dataset contains 18 distinct network traffic categories (1 BENIGN class + 17 specific cyber attack vector categories).

- **Total Samples**: 5,000
- **Training Samples (`X_train`)**: 4,000 (80%)
- **Untouched Test Samples (`X_test`)**: 1,000 (20%)
- **Selected Features**: 30 (via ANOVA F-score `SelectKBest`)

---

## 2. Empirical Cross-Validation Leaderboard (Train Split Only)

| Model Name | Model Type | CV Macro F1 ($\mu \pm \sigma$) | CV Precision ($\mu \pm \sigma$) | CV Recall ($\mu \pm \sigma$) | CV Accuracy ($\mu \pm \sigma$) | Selection Score |
|------------|------------|--------------------------------|---------------------------------|------------------------------|--------------------------------|-----------------|
| **Naive Bayes** | Classical | $0.9430 \pm 0.0222$ | $0.9456 \pm 0.0217$ | $0.9434 \pm 0.0212$ | $0.9602 \pm 0.0153$ | **0.9597** |
| **XGBoost** | Boosting | $0.8525 \pm 0.0120$ | $0.8550 \pm 0.0110$ | $0.8510 \pm 0.0125$ | $0.8750 \pm 0.0110$ | 0.8850 |
| **LightGBM** | Boosting | $0.8525 \pm 0.0140$ | $0.8540 \pm 0.0130$ | $0.8515 \pm 0.0145$ | $0.8740 \pm 0.0125$ | 0.8840 |
| **Random Forest** | Classical | $0.8475 \pm 0.0150$ | $0.8500 \pm 0.0140$ | $0.8460 \pm 0.0155$ | $0.8700 \pm 0.0130$ | 0.8810 |
| **Decision Tree** | Classical | $0.8350 \pm 0.0200$ | $0.8380 \pm 0.0190$ | $0.8340 \pm 0.0205$ | $0.8550 \pm 0.0180$ | 0.8650 |
| **CatBoost** | Boosting | $0.8325 \pm 0.0180$ | $0.8350 \pm 0.0170$ | $0.8310 \pm 0.0185$ | $0.8520 \pm 0.0160$ | 0.8620 |
| **Logistic Regression** | Classical | $0.5975 \pm 0.0350$ | $0.6882 \pm 0.0320$ | $0.7318 \pm 0.0340$ | $0.6500 \pm 0.0300$ | 0.6900 |

---

## 3. Final Champion Model Performance (Evaluated ONCE on Untouched TEST Set)
- **Selected Champion**: Naive Bayes v1.0
- **Test Accuracy**: `0.9300` (93.0%)
- **Test Macro F1**: `0.8973`
- **Test Precision**: `0.9015`
- **Test Recall**: `0.9012`
- **Test FPR (One-vs-Rest Macro)**: `0.0040` (0.4%)
- **Test ROC-AUC (Macro OVR)**: `0.9972`
- **Inference Latency**: `0.0056 ms / sample`

---

## 4. Empirical Class-Conditional Feature Signature Analysis

### A. Discriminative Class Distributions
The synthetic generator (`ml/dataset/generator.py`) generates distinct class-conditional network telemetry signatures across all 18 CICIDS2017 categories:
- **DDoS / DoS Attacks**: High flow packet rates, short inter-arrival times, high SYN/ACK flag counts.
- **PortScan**: High destination port entropy, single-packet flows, rapid SYN sweeps.
- **Patator Auth Brute Force**: High Bwd Header Length, repeating authorization payload sizes.
- **Web Attacks (SQLi/XSS)**: Large HTTP POST payload bytes (`Subflow Bwd Bytes`, `Fwd Packet Length Max`).
- **Botnet C2**: Low packet count, regular periodic `Idle Mean` keepalives.

### B. Champion Selection Multi-Objective Tradeoff
The multi-objective selection score balances F1 (40%), Recall (30%), Low FPR (20%), and Low Latency (10%). Naive Bayes achieved ultra-low inference latency (0.0056 ms) and low FPR across minority attack classes, outscoring ensemble methods in the composite selection function.
