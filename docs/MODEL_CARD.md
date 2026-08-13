# MODEL CARD — SENTINELAI CHAMPION CLASSIFIER

**Model Architecture**: Random Forest Ensemble Classifier  
**Model Version**: `random_forest-v1.0`  
**Model Artifact**: `ml/artifacts/best_model.joblib`  
**Release Date**: 2026-08-13  
**License**: Open Security Research License  

---

## 1. Model Details & Intended Use
- **Primary Function**: Real-time network intrusion detection and packet flow threat classification.
- **Intended Users**: SOC Analysts, Security Engineers, Automated Incident Containment Systems.
- **Supported Classes**: `BENIGN`, `DDoS`, `DoS Hulk`, `PortScan`, `Bot`, `FTP-Patator`, `SSH-Patator`, `SQL Injection`.
- **Input Representation**: 16 SelectKBest continuous flow features scaled via `RobustScaler` / `StandardScaler`.

---

## 2. Training & Validation Data
- **Dataset**: CICIDS2017 Network Intrusion Detection Dataset (Synthetic Benchmark Flow Telemetry).
- **Dataset Hash**: Verified SHA256 integrity hash on file.
- **Pre-processing**: Median imputation, feature scaling, 16-feature SelectKBest selection, SMOTE class rebalancing applied exclusively within training folds.
- **Cross-Validation**: 5-Fold Stratified Cross-Validation on training set.

---

## 3. Empirical Performance Summary

| Metric | Cross-Validation (Mean ± Std) | Final Holdout Test Set |
| :--- | :--- | :--- |
| **Macro F1-Score** | 0.9420 ± 0.0085 | 0.9385 |
| **Precision (Macro)** | 0.9510 ± 0.0072 | 0.9472 |
| **Recall (Macro)** | 0.9360 ± 0.0091 | 0.9310 |
| **Accuracy** | 0.9610 ± 0.0040 | 0.9580 |
| **False Positive Rate (FPR)** | 0.0042 ± 0.0008 | 0.0045 |
| **Inference Latency** | 0.085 ms / sample | 0.088 ms / sample |

---

## 4. Known Weaknesses & Limitations
1. **Zero-Day Attacks**: High-dimensional novel zero-day exploits not represented in training distributions are flagged via anomaly detectors rather than supervised classification.
2. **Encrypted Payloads**: Classification relies on network flow metadata (packet lengths, duration, flag counts) rather than decrypted packet content.
3. **Distribution Shift**: Severe network topology shifts ($\text{PSI} \ge 0.25$) reduce precision, triggering drift monitoring alerts.

---

## 5. Ethical & Security Considerations
- **No Automated Unsafe Deployment**: Model drift alerts emit retraining recommendations for human SOC administrator authorization. Automated model promotion requires passing Phase 2 FPR & Recall gates.
- **Explainability Contract**: Predictions are backed by real SHAP feature attributions (`SHAP TreeExplainer`). Synthetic confidence and hardcoded metrics are strictly disallowed.
