<div align="center">

```
  ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗      █████╗ ██╗
  ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     ██╔══██╗██║
  ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     ███████║██║
  ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     ██╔══██║██║
  ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗██║  ██║██║
  ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝
```

# SentinelAI – Intelligent Network Intrusion Detection & Threat Analytics Platform

**Research-Verified AI/ML Network Intrusion Detection & Security Operations Platform Prototype**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1-EE4C2C.svg?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Docker Compose](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

[Architecture](#-system-architecture) • [Key Features](#-key-features) • [ML Leaderboard](#-machine-learning-leaderboard) • [Quickstart](#-quickstart--installation) • [API Contract](#-api--websocket-contract) • [Documentation](#-documentation)

---
</div>

> [!NOTE]
> **SentinelAI** is an AI-powered Network Intrusion Detection System (NIDS) prototype designed to evaluate network flow statistics against benchmark intrusion datasets (such as **CICIDS2017**). It evaluates 12 Machine Learning and Deep Learning classifiers using a leakage-free split-first pipeline, with real SHAP explainability, multi-metric promotion gates, and an interactive React SOC dashboard operating in **DEMO MODE**.

---

## 🏛️ System Architecture

```mermaid
flowchart TB
    subgraph Ingestion ["1. Data & Traffic Ingestion"]
        A[Raw PCAP / CSV Upload] --> C[Feature Extractor]
        B[Live WebSockets Telemetry] --> C
    end

    subgraph Preprocessing ["2. ML Pipeline & Preprocessing"]
        C --> D[Median Imputer & Scaler]
        D --> E[SMOTE Class Balancer]
        E --> F[SelectKBest Feature Isolator]
    end

    subgraph Inference ["3. 12-Model Inference Engine"]
        F --> G1[Boosting: XGBoost / LightGBM / CatBoost]
        F --> G2[Classical: Random Forest / Decision Tree / SVM]
        F --> G3[DeepNet: PyTorch 1D-CNN / LSTM / Autoencoder]
    end

    subgraph Explainability ["4. Explainable AI (XAI)"]
        G1 --> H[SHAP & LIME Feature Attribution]
    end

    subgraph SOC ["5. Security Operations & Action"]
        H --> I1[Cyberpunk React SPA Dashboard]
        H --> I2[1-Click Automated Firewall Drop Rule]
        H --> I3[Automated ReportLab PDF Exporter]
    end
```

---

## ⚡ Key Features & Innovations

### 🧠 12-Model Machine Learning Leaderboard
- **Ensemble Boosting**: CatBoost *(current champion — see `results/EXP-2026-002/provenance.json`)*, XGBoost, LightGBM
- **Classical Classifiers**: Random Forest, Decision Tree, Logistic Regression, SVM, KNN, Naive Bayes
- **Deep Learning Architecture**: PyTorch 1D-CNN, Recurrent LSTM, Deep Anomaly Autoencoder

### 🔍 Explainable AI (XAI with SHAP & LIME)
- Eliminates "black-box" decision making by exposing feature importance plots for every inspected packet flow.
- Highlights exact feature contributions (e.g. `Flow Packets/s`, `SYN Flag Count`, `Packet Length Mean`).

### 🌐 Live 2D Network Node Topology Canvas
- Renders real-time particle flows across infrastructure nodes (`EDGE-FW-01`, `APP-SRV-01`, `CORE-DB-01`, `EXT-ATTACKER`).
- Visualizes normal background network traffic vs. **neon crimson intrusion streams**.

### 🌍 Global Threat Origin Matrix
- Real-time geolocation breakdown of external attacker IPs (US, RU, CN, DE, BR) with active regional geoblocking status.

### 🛡️ 1-Click Automated Threat Remediation
- Security Analysts can dispatch automated containment playbooks directly from the dashboard:
  - **Perimeter Firewall Drop Rule**: Injects instant drop ACLs across edge gateways.
  - **VLAN Quarantine Sandbox**: Moves infected host devices to isolated VLAN 999.

### 📄 Executive Report Exporter
- Automated **ReportLab PDF Exporter** and **OpenPyXL Excel Workbook Generator** for compliance reporting.

---

## 📊 Experiment Results & Benchmark Provenance

### 1. Current Live Experiment (`EXP-2026-002`)
The current local reproducible benchmark runs 100% leakage-free 3-fold Stratified CV on training data with an isolated test set evaluation:
- **Champion Model**: `CatBoost` (`catboost-v1.0`)
- **Dataset**: `synthetic_cicids2017_benchmark` (Hash: `62aa92a7d54fe464`, Seed: `42`)
- **CV Macro F1**: `0.9301` (std: `0.0245`)
- **Final Test Macro F1**: `0.9329` | **Accuracy**: `0.9600` | **FPR**: `0.0023` | **ROC-AUC**: `0.9996`
- **Provenance Manifest**: [`results/EXP-2026-002/provenance.json`](results/EXP-2026-002/provenance.json) & [`ml/artifacts/metadata.json`](ml/artifacts/metadata.json)

### 2. Historical Literature Reference Benchmarks (`EXP-2026-001`)
> [!NOTE]
> The metrics listed below represent historical reference baselines on the full real **CICIDS2017** benchmark dataset.
> Source: [`research/reference/historical_benchmarks.json`](research/reference/historical_benchmarks.json) & [`results/archive/EXP-2026-001/`](results/archive/EXP-2026-001/).

| Model | Model Type | Accuracy | F1-Score | Precision | Recall | ROC-AUC | Role |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost** | Boosting | **0.9912** | **0.9901** | **0.9920** | **0.9882** | **0.997** | 👑 Historical Reference Baseline |
| **CatBoost** | Boosting | 0.9905 | 0.9892 | 0.9910 | 0.9874 | 0.996 | Historical Reference |
| **LightGBM** | Boosting | 0.9895 | 0.9880 | 0.9899 | 0.9861 | 0.995 | Historical Reference |
| **Random Forest** | Ensemble | 0.9885 | 0.9872 | 0.9890 | 0.9854 | 0.994 | Historical Reference |
| **LSTM** | Deep Learning | 0.9875 | 0.9860 | 0.9880 | 0.9840 | 0.993 | Historical Reference |
| **1D-CNN** | Deep Learning | 0.9860 | 0.9845 | 0.9870 | 0.9820 | 0.992 | Historical Reference |
| **Autoencoder** | Deep Learning | 0.9790 | 0.9770 | 0.9800 | 0.9740 | 0.987 | Historical Reference |
| **Decision Tree** | Classical | 0.9740 | 0.9721 | 0.9750 | 0.9692 | 0.981 | Historical Reference |
| **KNN** | Classical | 0.9610 | 0.9580 | 0.9630 | 0.9531 | 0.978 | Historical Reference |
| **SVM** | Classical | 0.9520 | 0.9490 | 0.9550 | 0.9431 | 0.972 | Historical Reference |
| **Logistic Regression** | Linear | 0.9250 | 0.9210 | 0.9280 | 0.9142 | 0.950 | Historical Reference |
| **Naive Bayes** | Probabilistic | 0.8840 | 0.8790 | 0.8890 | 0.8692 | 0.921 | Historical Reference |

---

## 🚀 Quickstart & Installation

### Option A: Docker Compose (Production Mode)
```bash
# Clone the repository
git clone https://github.com/ANURAG20042006/SENTINELAI.git
cd SENTINELAI

# Spin up PostgreSQL 16, Redis 7, Uvicorn Backend & Nginx Gateway
docker-compose -f docker/docker-compose.yml up -d --build
```
*Access UI at [http://localhost](http://localhost) and API Docs at [http://localhost:8000/docs](http://localhost:8000/docs).*

---

### Option B: Bare-Metal Setup (Development Mode)

#### 1. Backend & ML Setup
```bash
# Create and activate virtual environment (Python 3.11.x)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install exact declared dependencies (enforces scikit-learn 1.6.1 for ML artifacts)
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run ML pipeline & artifact generator
python -m ml.train_pipeline

# Start FastAPI server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend React SPA Setup
```bash
cd frontend
npm install
npm run dev
```
*Access Frontend at [http://localhost:5173](http://localhost:5173).*

---

## 🔑 Demo Role Credentials

Default user accounts are initialized on startup. Passwords can be configured in your local `.env` configuration file using the variables below:

| Role | Username | Environment Variable (Configure in `.env`) | Privileges |
| :--- | :--- | :--- | :--- |
| 👑 **Administrator** | `admin` | `SENTINEL_ADMIN_PASSWORD` | Full System Control & Model Retraining |
| 🔬 **Security Analyst** | `analyst` | `SENTINEL_ANALYST_PASSWORD` | Traffic Inspection, Playbooks & Reports |
| 👁️ **Operations Viewer** | `viewer` | `SENTINEL_VIEWER_PASSWORD` | Read-Only Dashboard Monitoring |

---

## 📚 Complete Project Documentation

Exhaustive technical documentation is available in the [`docs/`](docs/) directory:

- 🏗️ [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) – System Topology & Data Flow
- 💾 [`docs/DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md) – Entity-Relationship Database Schemas
- 📐 [`docs/UML_DIAGRAMS.md`](docs/UML_DIAGRAMS.md) – Class, Sequence, & Activity Diagrams
- 🛠️ [`docs/INSTALLATION.md`](docs/INSTALLATION.md) – Local Setup Guide
- 🚀 [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) – Nginx & SSL/TLS Deployment Guide
- 📖 [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) – REST API & WebSockets Contract
- 👤 [`docs/USER_MANUAL.md`](docs/USER_MANUAL.md) – Security Operations Manual
- 🎓 [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) – Academic Thesis Document
- 🎤 [`docs/PRESENTATION_NOTES.md`](docs/PRESENTATION_NOTES.md) – Viva Defense Script & Q&A
- 🏆 [`docs/PROJECT_EVALUATION_REPORT.md`](docs/PROJECT_EVALUATION_REPORT.md) – Comprehensive Evaluation & Review Report

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <sub>Built with ❤️ by Senior Engineering Team. SentinelAI © 2026</sub>
</div>
