# 🎓 SentinelAI Project Viva & Executive Presentation Guide

## 1. Project Overview & Elevator Pitch

> **"SentinelAI is an enterprise-grade, AI-powered Network Intrusion Detection System (NIDS) designed to detect, classify, and mitigate cyber threats in real time using 12 machine learning & deep learning models trained on the benchmark CICIDS2017 dataset."**

---

## 2. Key Technical Stack & Architecture

```
[ Incoming Network Traffic Packets ]
                 │
                 ▼
[ FastAPI 0.141 Asynchronous Backend Engine ]
                 │
  ├── ML Inference Engine (XGBoost, Random Forest, 1D-CNN)
  ├── SQLite / PostgreSQL Async Database Storage
  └── Real-Time WebSocket Telemetry Stream (/ws/threats)
                 │
                 ▼
[ React 18 + TypeScript + Tailwind CSS Operations Center Dashboard ]
```

- **Backend**: FastAPI 0.141 (Python 3.11+), Async SQLAlchemy 2.0 ORM, PyTorch 2.0, Scikit-learn, WebSockets.
- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts, Lucide Icons, Glassmorphism UI.
- **Database**: SQLite (Development) / PostgreSQL (Production) with automatic table seeding.
- **Machine Learning**: 12 classifiers trained on 78-feature packet flow vectors.

---

## 3. Machine Learning Models & Performance Benchmarks

> [!NOTE]
> The accuracy figures below are from the **prototype development phase** (not from the current reproducible experiment suite).
> **For empirically generated, current results**, see `results/EXP-2026-002/baseline_comparison.csv`, `results/EXP-2026-002/research_summary.json`, and `results/EXP-2026-002/provenance.json`.
> Examiners should direct performance questions to these live-generated artifacts.

| Model Name | Model Type | Primary Use Case |
| :--- | :--- | :--- |
| **Random Forest** | Classical Ensemble | Default production classifier |
| **XGBoost** | Gradient Boosting | Top accuracy on structured tabular flow data |
| **LightGBM** | Gradient Boosting | High-speed low-latency threat classification |
| **1D-CNN** | Deep Learning | Sequential feature pattern detection |
| **Autoencoder** | Neural Anomaly | Zero-Day unknown threat anomaly detection |



## 4. Top Anticipated Viva Questions & Best Answers

### Q1: Why did you choose FastAPI instead of Django or Flask?
> **Answer**: FastAPI is built natively on ASGI (Asynchronous Server Gateway Interface) using `async/await`. This provides 3x to 5x higher throughput for streaming real-time network packet inspection via WebSockets compared to WSGI frameworks like Flask.

### Q2: How does your system handle Zero-Day attacks that haven't been seen before?
> **Answer**: We employ an **Autoencoder Neural Network** trained exclusively on normal benign traffic. When unknown traffic exhibits high reconstruction error above a statistical threshold, it is flagged as an anomalous zero-day threat even if traditional signature rules do not match.

### Q3: How do you prevent unauthorized access to sensitive remediation actions?
> **Answer**: We enforce strict **Role-Based Access Control (RBAC)** via signed JWT (JSON Web Tokens). Only users with `admin` or `analyst` roles can trigger remediation playbooks or retrain models.

---

## 5. Quick Live Demo Script (3-Minute Presentation)

1. **Launch**: Double click `start_all.bat` on Desktop ➔ Opens `http://localhost:5173/`.
2. **Login**: Click **`Admin`** 1-Click login button ➔ Sign in.
3. **Master Dashboard**: Point out the **Live Model Selector** dropdown, **Global Attack Map**, and **Real-Time Telemetry Cards**.
4. **Live Prediction**: Go to **Live Prediction** ➔ Click **Test Sample Vector** ➔ View confidence score and severity.
5. **PDF & CSV Export**: Go to **Alert History** ➔ Click **Export CSV** to demonstrate report generation.
