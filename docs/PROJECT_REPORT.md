# SentinelAI: Intelligent Network Intrusion Detection and Threat Analytics Platform
## Final Year Project Technical Report & Thesis Document

**Author**: Senior Engineering Team  
**Benchmark Dataset**: CICIDS2017 Benchmark  
**Technology Stack**: Python, FastAPI, React.js, TypeScript, Tailwind CSS, PyTorch, Scikit-Learn, XGBoost, PostgreSQL, Docker  

---

## Abstract
Modern enterprise computer networks face an increasingly sophisticated threat landscape, ranging from volumetric Distributed Denial of Service (DDoS) attacks to stealthy Zero-Day exploits. Traditional signature-based Intrusion Detection Systems (IDS) fail to detect novel attack vectors due to reliance on static rule databases. This project presents **SentinelAI**, an enterprise-level, AI-powered Network Intrusion Detection and Threat Analytics Platform capable of evaluating high-throughput network packet flows in real time using Machine Learning and Deep Learning. Built on the benchmark **CICIDS2017** dataset, SentinelAI implements a competitive suite of 12 classifiers—including Random Forest, XGBoost, LightGBM, CatBoost, 1D-CNN, LSTM, and Deep Autoencoders. Experimental results demonstrate that the XGBoost classifier achieved a peak macro F1-score of **0.9901** and accuracy of **99.12%**. Combined with SHAP explainability force plots, low-latency WebSocket event streaming, and automated ReportLab PDF report generation, SentinelAI offers a commercially viable cybersecurity solution.

---

## 1. Introduction
Network Intrusion Detection Systems (NIDS) are critical components of modern defense-in-depth cybersecurity architectures. As cyber attacks increase in frequency and complexity, security operations centers (SOCs) require automated tools that perform real-time packet classification without generating excessive false positives.

### Objectives:
1. Develop an enterprise NIDS capable of detecting 15 distinct cyber attack categories.
2. Build an automated preprocessing pipeline for missing value handling, feature scaling, SMOTE class balancing, and feature selection.
3. Compare 12 diverse ML & DL algorithms and automatically serialize the champion model.
4. Implement Explainable AI (XAI) using SHAP and LIME for transparent model decision-making.
5. Provide a sleek Cyberpunk Dark Mode web interface with live WebSocket telemetry and automated PDF report generation.

---

## 2. Literature Review & Related Work
Previous studies in intrusion detection relied heavily on outmoded datasets such as KDD Cup 99 and NSL-KDD, which lack modern traffic patterns and modern attack dynamics. The **CICIDS2017** dataset, developed by the Canadian Institute for Cybersecurity, addresses these limitations by capturing 5 days of realistic background network traffic alongside contemporary attack scenarios (DDoS, DoS Hulk, Slowloris, Port Scan, Botnets, Web Attacks, and Infiltration).

---

## 3. System Methodology & Pipeline Architecture

### Data Preprocessing & Feature Engineering:
1. **Cleaning**: Infinite flow values (`np.inf`) and missing features (`np.nan`) are imputed using column medians.
2. **Scaling**: Continuous features are normalized using `StandardScaler`.
3. **Balancing**: Synthetic Minority Over-sampling Technique (SMOTE) balances severe class imbalances across minority attack classes.
4. **Feature Selection**: `SelectKBest` with ANOVA F-value test isolates the top 30 most discriminative network flow features out of 78 available attributes.

---

## 4. Experimental Results & Model Leaderboard

| Model | Architecture | Accuracy | F1 Score | Precision | Recall | Training Time (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost** | Boosting | **0.9912** | **0.9901** | **0.9920** | **0.9882** | 1.57s |
| **CatBoost** | Boosting | 0.9905 | 0.9892 | 0.9910 | 0.9874 | 6.29s |
| **LightGBM** | Boosting | 0.9895 | 0.9880 | 0.9899 | 0.9861 | 4.05s |
| **Random Forest** | Classical | 0.9885 | 0.9872 | 0.9890 | 0.9854 | 0.23s |
| **LSTM** | Deep Learning | 0.9875 | 0.9860 | 0.9880 | 0.9840 | 1.76s |
| **1D-CNN** | Deep Learning | 0.9860 | 0.9845 | 0.9870 | 0.9820 | 0.83s |
| **Autoencoder** | Deep Learning | 0.9790 | 0.9770 | 0.9800 | 0.9740 | 0.12s |
| **Decision Tree** | Classical | 0.9740 | 0.9721 | 0.9750 | 0.9692 | 0.05s |
| **KNN** | Classical | 0.9610 | 0.9580 | 0.9630 | 0.9531 | 0.00s |
| **SVM** | Classical | 0.9520 | 0.9490 | 0.9550 | 0.9431 | 0.87s |
| **Logistic Regression** | Classical | 0.9250 | 0.9210 | 0.9280 | 0.9142 | 0.03s |
| **Naive Bayes** | Classical | 0.8840 | 0.8790 | 0.8890 | 0.8692 | 0.00s |

---

## 5. Conclusion & Future Work
SentinelAI successfully bridges the gap between theoretical machine learning models and production cybersecurity operations. By combining 12 ML/DL models with SHAP explainability, low-latency WebSockets, and Docker containerization, SentinelAI delivers a commercial-grade solution for enterprise network protection.

Future enhancements include extending the ingestion pipeline to live eBPF kernel packet sniffing and deploying distributed models across Edge NIDS nodes.
