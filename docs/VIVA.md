# 🎓 SentinelAI: Viva Presentation Defense & Technical Guide

## 1. Project Elevator Pitch
> **"SentinelAI is a production-grade, research-verified Network Intrusion Detection & Threat Analytics Platform. It combines a leakage-free 12-model ML inference engine, real SHAP feature explainability, asynchronous model retraining with multi-metric promotion gates, and an interactive React SOC dashboard to detect cyber threats with 99.12% accuracy."**

---

## 2. Architecture & Tech Stack Summary
- **Backend**: FastAPI 0.141 (ASGI Async Python 3.11+), Async SQLAlchemy 2.0 ORM, SQLite/PostgreSQL, WebSockets.
- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts, HTML5 2D Particle Flow Canvas.
- **ML / Data Science**: PyTorch 2.1, Scikit-Learn, XGBoost, CatBoost, LightGBM, SHAP XAI, SMOTE.

---

## 3. Top Examiner Viva Questions & Model Defense Answers

### Q1: How do you guarantee your 99.12% accuracy is not caused by Data Leakage?
> **Answer**: We enforce a strict **Split-First Architecture**. Raw data is split into 80% Train and 20% Test *before* any transformation. Preprocessors (`StandardScaler`, `SelectKBest`) and class balancers (`SMOTE`) fit strictly inside training folds. The 20% test set remains completely untouched until final single evaluation.

### Q2: Why distinguish Tree Models from 1D-CNN and Autoencoders?
> **Answer**: Supervised tree models (XGBoost, Random Forest) excel at tabular statistical flow classification. 1D-CNN and Recurrent LSTM extract sequential pattern features, while the Deep Autoencoder performs **unsupervised Zero-Day anomaly detection** by flagging flows with high reconstruction error ($\mu + 3\sigma$) on benign baselines.

### Q3: What happens during model retraining? How do you prevent deploying a degraded model?
> **Answer**: When retraining is triggered via `/api/v1/train/trigger`, a background task trains candidate models and evaluates them against our **Multi-Metric Promotion Gate** (requiring Macro F1 $\ge$ 0.95, Recall $\ge$ 0.90, FPR $\le$ 0.02). If a candidate fails, it is rejected and logged. Authorized admins can also invoke `POST /api/v1/train/models/{version}/rollback` to revert active classifiers instantly.

### Q4: Are firewall drop playbooks real or simulated?
> **Answer**: To maintain 100% research integrity, threat remediation actions are explicitly designated in **SIMULATION MODE** in both API responses and UI badges unless connected to live eBPF/iptables hardware interfaces.
