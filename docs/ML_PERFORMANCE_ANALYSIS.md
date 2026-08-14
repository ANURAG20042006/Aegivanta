# SentinelAI Empirical Machine Learning Performance & System Analysis

**Experiment Reference**: EXP-2026-002  
**Dataset Identifier**: `synthetic_cicids2017_benchmark` (Hash: `62aa92a7d54fe464`, 500 samples, 30 selected features, 18 target attack classes)  
**Methodological Protocol**: Decoupled split-first architecture with fold-local scaling, SelectKBest feature selection, and fold-local SMOTE. Single evaluation on frozen untouched test set.

---

## 1. Class Distribution & Benchmark Overview
The benchmark dataset contains 18 distinct network traffic categories (1 BENIGN class + 17 specific cyber attack vector categories).

- **Total Samples**: 500
- **Training Samples (`X_train`)**: 400 raw / 2,574 post-SMOTE (80%)
- **Untouched Test Samples (`X_test`)**: 100 (20%)
- **Selected Features**: 30 (via ANOVA F-score `SelectKBest(k=30)`)

---

## 2. Empirical Cross-Validation Leaderboard (Train Split Only)

| Model Name | Model Type | CV Macro F1 ($\mu \pm \sigma$) | CV Precision ($\mu \pm \sigma$) | CV Recall ($\mu \pm \sigma$) | CV Accuracy ($\mu \pm \sigma$) | Selection Score |
|------------|------------|--------------------------------|---------------------------------|------------------------------|--------------------------------|-----------------|
| **CatBoost** | Boosting | **$0.9301 \pm 0.0245$** | **$0.9405 \pm 0.0190$** | **$0.9323 \pm 0.0292$** | **$0.9625 \pm 0.0148$** | **0.9512** (👑 Champion) |
| **Naive Bayes** | Classical | $0.9289 \pm 0.0349$ | $0.9477 \pm 0.0297$ | $0.9269 \pm 0.0369$ | $0.9576 \pm 0.0214$ | 0.9491 |
| **XGBoost** | Boosting | $0.9269 \pm 0.0213$ | $0.9350 \pm 0.0168$ | $0.9277 \pm 0.0277$ | $0.9475 \pm 0.0127$ | 0.9483 |
| **Random Forest** | Classical | $0.9255 \pm 0.0230$ | $0.9403 \pm 0.0168$ | $0.9240 \pm 0.0304$ | $0.9550 \pm 0.0128$ | 0.9447 |
| **Decision Tree** | Classical | $0.9169 \pm 0.0440$ | $0.9314 \pm 0.0395$ | $0.9202 \pm 0.0444$ | $0.9500 \pm 0.0187$ | 0.9422 |
| **KNN** | Classical | $0.9065 \pm 0.0069$ | $0.9128 \pm 0.0058$ | $0.9097 \pm 0.0109$ | $0.9375 \pm 0.0112$ | 0.9332 |
| **LightGBM** | Boosting | $0.9027 \pm 0.0623$ | $0.9109 \pm 0.0570$ | $0.9115 \pm 0.0554$ | $0.9375 \pm 0.0378$ | 0.9332 |
| **LSTM** | Deep Learning | $0.8912 \pm 0.0364$ | $0.9079 \pm 0.0157$ | $0.8905 \pm 0.0413$ | $0.9326 \pm 0.0195$ | 0.9228 |
| **1D-CNN** | Deep Learning | $0.8899 \pm 0.0325$ | $0.9009 \pm 0.0229$ | $0.8909 \pm 0.0341$ | $0.9300 \pm 0.0170$ | 0.9224 |
| **Logistic Regression** | Classical | $0.8736 \pm 0.0440$ | $0.8895 \pm 0.0182$ | $0.8917 \pm 0.0410$ | $0.8951 \pm 0.0514$ | 0.9157 |
| **SVM** | Classical | $0.8483 \pm 0.0515$ | $0.8832 \pm 0.0151$ | $0.8704 \pm 0.0508$ | $0.7779 \pm 0.1415$ | 0.8972 |

---

## 3. Final Champion Model Performance (Evaluated ONCE on Untouched TEST Set)
- **Selected Champion**: CatBoost v1.0 (`catboost.joblib` / `best_model.joblib`)
- **Test Accuracy**: `0.9600` (96.0%)
- **Test Macro F1**: `0.9329`
- **Test Precision**: `0.9333`
- **Test Recall**: `0.9389`
- **Test FPR (One-vs-Rest Macro)**: `0.0023` (0.23%)
- **Test ROC-AUC (Macro OVR)**: `0.9996`
- **Authoritative Inference Latency**: `0.0184 ms / sample`

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
The multi-objective selection score balances F1 (40%), Recall (30%), Low FPR (20%), and Low Latency (10%). CatBoost achieved the optimal balance with 0.9301 CV F1, 0.9625 CV Accuracy, 0.0022 CV FPR, and 0.0184 ms inference latency, outscoring candidate methods in the composite selection function.
