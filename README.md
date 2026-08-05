<div align="center">

# 🛡️ SentinelAI
### Intelligent Network Intrusion Detection & Threat Analytics Platform

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)
![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2-EE4C2C.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)

*An enterprise-grade, commercial AI cybersecurity product designed for real-time network traffic packet inspection, threat classification, and explainable AI analytics using the CICIDS2017 benchmark dataset.*

</div>

---

## 📌 Executive Overview

**SentinelAI** is an advanced Network Intrusion Detection System (NIDS) and Threat Analytics Platform designed to detect, analyze, and visualize cyber threats in real time. Powered by an ensemble suite of **12 Machine Learning & Deep Learning classifiers**, SentinelAI inspects high-throughput network packet flows, categorizing traffic into 15 distinct categories (including DDoS, DoS Hulk, Port Scans, SQL Injection, Ransomware, and Zero-Day Anomalies).

Designed with a sleek **Cyberpunk Dark Mode UI**, SentinelAI delivers real-time WebSocket telemetry, interactive confusion matrices, ROC curves, SHAP explainability force plots, and automated ReportLab PDF executive report generation.

---

## ✨ Key Platform Features

- 🧠 **12 ML/DL Classifier Suite**: Random Forest, XGBoost, LightGBM, CatBoost, Decision Tree, Logistic Regression, SVM, KNN, Naive Bayes, 1D-CNN, LSTM, and Deep Autoencoders.
- 📊 **CICIDS2017 Benchmark Pipeline**: Automated missing value imputation, infinite value cleanup, `StandardScaler` normalization, SMOTE class balancing, and `SelectKBest` feature selection across 78 network features.
- ⚡ **Real-Time Telemetry & WebSockets**: Low-latency WebSocket event stream (`/ws/threats`) delivering real-time packet feeds and toast alert notifications for high-risk flows.
- 🔍 **Drag-and-Drop Traffic Inspector**: Inspect individual packet feature vectors or upload multi-megabyte network traffic capture CSV files with instant row-by-row malicious packet highlighting.
- 📈 **Explainable AI (XAI)**: Integrated SHAP (SHapley Additive exPlanations) and LIME feature attribution plots explaining *why* a specific flow was flagged.
- 📄 **Executive PDF & Excel Exporter**: Automated ReportLab PDF generator rendering dark cybersecurity executive summaries and OpenPyXL Excel workbooks.
- 🔒 **Enterprise RBAC Authentication**: OAuth2 JWT authentication supporting **Admin**, **Analyst**, and **Viewer** roles with comprehensive operation audit logging.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend SPA** | React 18, TypeScript 5.2, Vite, Tailwind CSS v3, Material UI v5, Chart.js, Framer Motion |
| **Backend Core** | Python 3.11, FastAPI, Pydantic v2, Uvicorn ASGI Server |
| **Database & Cache** | PostgreSQL 16 (Async SQLAlchemy 2.0 ORM), Redis 7 |
| **Machine Learning** | Scikit-Learn, PyTorch, XGBoost, LightGBM, CatBoost, SHAP, LIME, Joblib |
| **Report Engine** | ReportLab (PDF), OpenPyXL (Excel) |
| **DevOps** | Docker, Docker Compose, Nginx, GitHub Actions |

---

## ⚡ Quickstart Guide (Local Development)

### 1. Clone & Set Up Environment Variables
```bash
git clone https://github.com/your-org/sentinelai.git
cd sentinelai
cp .env.example .env
```

### 2. Launch using Docker Compose (Recommended)
```bash
# On Linux / macOS
chmod +x docker/deployment.sh
./docker/deployment.sh

# On Windows PowerShell
.\docker\deployment.ps1
```

Access the platform interfaces:
- 🌐 **Frontend Dashboard**: [http://localhost:80](http://localhost:80) or [http://localhost:5173](http://localhost:5173)
- 🔌 **FastAPI REST API Specs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🔑 **Default Admin Credentials**: `admin` / `AdminSecure2026!` (Anurag Rai)
- 👥 **Co-Admin Account**: `anshika` / `AnshikaSecure2026!` (Anshika Mishra)

---

## 📁 Repository Folder Structure

```
major project/
├── backend/            # FastAPI application, routers, services, ORM models
├── frontend/           # React + TypeScript Vite SPA application & dark theme UI
├── ml/                 # ML/DL training pipeline, models, preprocessor, SHAP explainer
├── database/           # SQL schemas, seed scripts, ER specs
├── docker/             # Dockerfiles, docker-compose.yml, Nginx gateway, deploy scripts
├── docs/               # Comprehensive documentation & architecture specs
├── tests/              # Pytest suite & end-to-end integration test runner
├── .env.example        # Environment variable template
├── LICENSE             # MIT License
└── README.md           # Master Documentation
```

---

## 📜 Documentation Directory

For in-depth guides, consult the dedicated documentation files:
- 📘 [`docs/ARCHITECTURE.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/ARCHITECTURE.md) - Deep Architectural Specifications
- 🟢 [`docs/INSTALLATION.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/INSTALLATION.md) - Step-by-Step Local Setup Guide
- 🚀 [`docs/DEPLOYMENT.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/DEPLOYMENT.md) - Production Docker & Nginx Deployment Guide
- 📡 [`docs/API_DOCUMENTATION.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/API_DOCUMENTATION.md) - REST API & WebSockets Contract
- 📖 [`docs/USER_MANUAL.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/USER_MANUAL.md) - Analyst & Administrator Operation Guide
- 🎓 [`docs/PROJECT_REPORT.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/PROJECT_REPORT.md) - Final Year Project Academic Thesis
- 🎤 [`docs/PRESENTATION_NOTES.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/PRESENTATION_NOTES.md) - Presentation Script & Viva Defense Q&A

---

## 📄 License

This project is licensed under the MIT License - see the [`LICENSE`](file:///c:/Users/NJ542WS/Desktop/major%20project/LICENSE) file for details.
