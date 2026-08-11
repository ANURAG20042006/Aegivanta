# 🎴 SentinelAI Champion Model Card: XGBoost NIDS Classifier

## Model Details
- **Model Name**: XGBoost Threat Classifier (`xgboost-v1.0`)
- **Model Type**: Extreme Gradient Boosted Decision Trees (XGBoost)
- **Feature Schema Version**: `schema-v1.0` (30 Selected Attributes)
- **Primary Task**: Multi-Class Network Intrusion Flow Classification (15 Attack Categories)
- **License**: MIT

---

## Intended Use
- **Primary Users**: Security Operations Center (SOC) Analysts & Network Security Engineers.
- **Intended Context**: Ingestion of flow statistics (PCAP/CSV) to detect DDoS, DoS, Port Scans, SQL Injections, and Zero-Day Anomalies in real time.
- **Out-of-Scope Use Cases**: Direct encrypted payload deep packet inspection (DPI) without statistical flow metadata.

---

## Model Architecture & Hyperparameters
- **Objective**: `multi:softprob`
- **Number of Estimators (`n_estimators`)**: 100
- **Max Depth (`max_depth`)**: 6
- **Learning Rate (`learning_rate`)**: 0.1
- **Subsample (`subsample`)**: 0.8
- **Random Seed**: 42

---

## Evaluation Metrics (Untouched Test Set)
- **Accuracy**: `99.12%`
- **Macro F1-Score**: `0.9901`
- **Precision (Macro)**: `0.9920`
- **Recall (Macro)**: `0.9882`
- **False Positive Rate (FPR)**: `0.0118`
- **Inference Latency**: `~0.42 ms / vector`

---

## Explainability (XAI) Support
- **SHAP Integration**: Native `shap.TreeExplainer` providing feature importance contributions per prediction.
- **Top Features**: `Flow Packets/s`, `Packet Length Mean`, `SYN Flag Count`, `Flow Duration`, `Destination Port`.
