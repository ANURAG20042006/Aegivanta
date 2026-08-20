<div align="center">

```
   █████╗ ███████╗ ██████╗ ██╗██╗   ██╗ █████╗ ███╗   ██╗████████╗ █████╗ 
  ██╔══██╗██╔════╝██╔════╝ ██║██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗
  ███████║█████╗  ██║  ███╗██║██║   ██║███████║██╔██╗ ██║   ██║   ███████║
  ██╔══██║██╔══╝  ██║   ██║██║╚██╗ ██╔╝██╔══██║██║╚██╗██║   ██║   ██╔══██║
  ██║  ██║███████╗╚██████╔╝██║ ╚████╔╝ ██║  ██║██║ ╚████║   ██║   ██║  ██║
  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝
```

# Aegivanta – Enterprise AI-Powered Security Operations Platform

**Next-Generation AI-Native Cybersecurity, Threat Detection & Autonomous SOC Platform**

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
> **Rebranding & Identity Notice**: *SentinelAI* was the previous product name. The platform is officially rebranded as **Aegivanta** — an Enterprise AI-Powered Security Operations Platform.
> 
> **Aegivanta** is an AI-native Network Intrusion Detection System (NIDS) & Next-Gen Security Operations Center (SOC) platform. It pairs a research-verified 12-Model ML/DL intrusion detection engine (featuring champion CatBoost with real SHAP explainability) with an **Advanced SOC Command Center** providing Protected Asset Management, Live Threat Alert Triage, Deterministic Incident Correlation, Attack Graph Analytics, Multi-Hop Lateral Movement Detection, Autonomous SOAR Response, and Multi-Factor Operational Risk Scoring.

---

## 🏢 Phase 4 Upgrade: Enterprise Multi-Tenant SaaS & Commercial Platform (v4.0.0)

Aegivanta (SentinelAI) v4.0 is fully commercialized into an Enterprise Multi-Tenant Cybersecurity SaaS Platform:

| Phase 4 SaaS Feature | Specifications & Security Architecture | Commercial Capabilities |
|---|---|---|
| **Multi-Tenancy & Isolation** | `Organization`, `Tenant`, `TenantMembership`, `TenantSettings` with `TenantContext` ContextVar | Zero cross-tenant data leakage, isolated workspaces, custom data retention |
| **Subscription Engine** | Free, Professional, Business, and Enterprise plans with `SubscriptionService` | Tier quotas (seats, telemetry volume, sensors), feature entitlements |
| **Customer API Keys** | 192-bit cryptographic entropy, SHA-256 hashed storage, scoped permissions | Machine-to-machine telemetry ingestion, SIEM integration, one-time secret display |
| **Usage Metering & Rate Limiting** | Non-blocking telemetry buffer, sliding-window `TenantRateLimiter` | HTTP 429 Retry-After enforcement, monthly rollup usage tracking |
| **Billing Abstraction & Webhooks** | `BillingProvider` abstraction, HMAC-SHA256 signature verification | Idempotent webhook handling, replay defense, provider-independent billing |
| **Telemetry Sensor Fleet** | Enrolled agents with crypto-hashed tokens, heartbeat monitoring | Endpoint & network taps, auto-offline detection, instant agent revocation |
| **Enterprise Connectors** | SIEM (Splunk, Elastic, Sentinel), Slack, generic Webhook, EDR | Automated critical incident dispatching, two-way containment |
| **Customer SaaS Portal** | React 18 frontend: Organizations, Billing, API Keys, Sensors, Integrations, Setup Wizard | Self-service team management, tier upgrades, key generation, guided onboarding |

---

## 🚀 Phase 3.3 Upgrade: Production Kubernetes & Deployment Hardening

SentinelAI includes production-grade Kubernetes manifests and container hardening under [`k8s/`](k8s/):

| Component | Manifest & Specifications | Security & Operational Hardening | Validation Status |
|---|---|---|:---:|
| **API Server** | [`deployment-api.yaml`](k8s/deployment-api.yaml) (3 Replicas) | Non-root UID 10001, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, capabilities dropped, `/tmp` `emptyDir` | 🟢 **Verified Statically & Locally** |
| **Stream Worker** | [`deployment-worker.yaml`](k8s/deployment-worker.yaml) (2 Replicas) | Dedicated stream consumer daemon (`backend.app.worker`), non-root UID 10001, graceful `SIGTERM` handling | 🟢 **Verified Statically & Locally** |
| **Redis Broker** | [`redis.yaml`](k8s/redis.yaml) (StatefulSet) | Non-root UID 999, password-authenticated from Secret, internal-only ClusterIP, Redis Streams | 🟢 **Verified Statically & Locally** |
| **Ingress & TLS** | [`ingress.yaml`](k8s/ingress.yaml) | TLS secret termination, WebSocket upgrades (`sentinelai-api:8000`), proxy buffer timeouts | 🟢 **Verified Statically** |
| **Autoscaling** | [`hpa.yaml`](k8s/hpa.yaml) | Independent HPA for API (2–10 pods, 70% CPU) and Worker (2–8 pods, 75% CPU) | 🟢 **Verified Statically** |
| **Disruption Safety**| [`pdb.yaml`](k8s/pdb.yaml) | PodDisruptionBudget ensuring `minAvailable: 1` during node maintenance | 🟢 **Verified Statically** |
| **Micro-Segmentation**| [`networkpolicy.yaml`](k8s/networkpolicy.yaml) | Ingress on 8000; Egress restricted to DNS (53), Redis (6379), and PostgreSQL (5432) | 🟢 **Verified Statically** |

---

## 🛡️ Phase 1 Upgrade: Advanced Dynamic SOC Platform

SentinelAI includes a full-featured Dynamic SOC platform layer built on top of the real-time ML inference pipeline:

| Phase 1 Feature | Backend Architecture & Engine | Frontend Workspace & Visuals | Status |
|---|---|---|:---:|
| **Protected Assets** | Asset inventory, criticality tiers, health metrics, soft-delete deactivation ([`assets.py`](backend/app/api/v1/assets.py)) | [`Assets.tsx`](frontend/src/pages/Assets.tsx) modal registration, environment filtering | ✅ **Verified** |
| **Live Event Stream** | Real-time WebSocket telemetry channel ([`/ws/threats`](backend/app/api/v1/websockets.py)) | [`LiveEventFeed.tsx`](frontend/src/components/dashboard/LiveEventFeed.tsx) on Dashboard | ✅ **Verified** |
| **Alerts & Triage** | Alert query, multi-state triage lifecycle, SHAP attribution link ([`alerts.py`](backend/app/api/v1/alerts.py)) | [`Alerts.tsx`](frontend/src/pages/Alerts.tsx) triage queue & SHAP viewer modal | ✅ **Verified** |
| **Incident Correlation** | Deterministic 300s sliding window correlation engine ([`correlation_engine.py`](backend/app/services/correlation_engine.py)) | Auto-grouped incident ledger with root alert references | ✅ **Verified** |
| **Attack Timeline** | Chronological attack progression ledger ([`incident_timeline.py`](backend/app/models/incident_timeline.py)) | [`AttackTimeline.tsx`](frontend/src/components/dashboard/AttackTimeline.tsx) vertical interactive timeline | ✅ **Verified** |
| **Dynamic Risk Engine** | Transparent multi-factor operational risk scoring ([`risk_engine.py`](backend/app/services/risk_engine.py)) | Real-time 0–100 risk gauges & transparent factor breakdown | ✅ **Verified** |
| **Incident Severity Policy** | Deterministic monotonic escalation policy: $\max(\text{Current}, \text{Alert}, \text{Risk})$ | Real-time severity badge elevation without accidental downgrade | ✅ **Verified** |
| **Incident Detail View** | Incident state machine (`DETECTED` $\rightarrow$ `CLOSED`), analyst notes ([`incidents.py`](backend/app/api/v1/incidents.py)) | [`IncidentDetail.tsx`](frontend/src/pages/IncidentDetail.tsx) deep investigation view | ✅ **Verified** |
| **Phase 1 Test Suite** | 259 automated tests spanning API, correlation, risk engine, security hardening, and ML | Full CI pytest suite with 0 failures | ✅ **Verified** |

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
        F --> G1[Boosting: XGBoost / LightGBM / CatBoost 👑]
        F --> G2[Classical: Random Forest / Decision Tree / SVM]
        F --> G3[DeepNet: PyTorch 1D-CNN / LSTM / Autoencoder]
    end

    subgraph Explainability ["4. Explainable AI (XAI)"]
        G1 --> H[SHAP & LIME Feature Attribution]
    end

    subgraph DynamicSOC ["5. Dynamic SOC Platform Layer (Phase 1)"]
        H --> J1[Asset Resolution & Criticality]
        J1 --> J2[Multi-Factor Risk Engine]
        J2 --> J3[Deterministic Incident Correlation Engine]
        J3 --> J4[Attack Timeline & State Machine]
        J4 --> J5[Live WebSocket Stream /ws/threats]
    end

    subgraph SOC ["6. Security Operations & Response"]
        J5 --> I1[Cyberpunk React SOC Dashboard & Live Feed]
        J5 --> I2[Alerts Triage & Incident Detail Investigation]
        J5 --> I3[Protected Assets Inventory Workspace]
        J5 --> I4[1-Click Automated Firewall / VLAN Quarantine]
        J5 --> I5[Automated ReportLab PDF / Excel Exporter]
    end
```

---

## ⚡ Key Features & Innovations

### 🛡️ Next-Gen SOC Operations Platform (Phase 1)
- **Asset Inventory & Health Monitoring**: Track enterprise assets (Websites, APIs, Databases, Endpoints, Network Devices) with environment tags (`production`, `staging`, `development`) and criticality tiers.
- **Deterministic Incident Correlation**: Automatically groups related alerts arriving within a 300-second window by target asset, destination IP, and attack vector.
- **Chronological Attack Timelines**: Interactive visual timelines detailing detection timestamps, correlated alerts, analyst triage logs, containment playbooks, and resolution.
- **Deterministic Multi-Factor Operational Risk Scoring**:
  $$\text{Operational Risk} = (\text{Threat Sev} \times 40.0) + (\text{Model Conf} \times 25.0) + (\text{Asset Crit} \times 20.0) + \left(\min\left(1.0, \frac{\text{Alert Count}}{10.0}\right) \times 15.0\right)$$
- **Explicit Incident Severity Policy**: Monotonic escalation guarantee preventing accidental downgrades during active incidents.

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
*Access UI at [http://localhost](http://localhost) and API Gateway Docs at [http://localhost/docs](http://localhost/docs) (served via Nginx reverse proxy; backend port 8000 remains internal).*

---

### Option B: Bare-Metal Setup (Development Mode)

The project is validated on Python 3.11.x (the lock file was generated against Python 3.11.5). Use that version for all local setup and testing.

#### 1. Backend & ML Setup
```bash
# Create and activate a fresh virtual environment using the supported Python version
py -3.11 -m venv .venv
.venv\Scripts\activate  # On macOS/Linux: source .venv/bin/activate

# Install the locked dependency set for a reproducible environment
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt

# Run ML pipeline & artifact generator
python -m ml.train_pipeline

# Start FastAPI server (development mode: direct access on port 8000)
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
*In bare-metal mode, access backend directly at [http://localhost:8000](http://localhost:8000) and Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).*

#### 2. Frontend React SPA Setup
```bash
cd frontend
# Reproducible dependency installation from package-lock.json
npm ci

# Start Vite React Dev Server
npm run dev

# Or build for production
npm run build
```
*Access Frontend at [http://localhost:5173](http://localhost:5173).*

#### 3. Automated Testing & Verification
Tests automatically run against an isolated session-scoped temporary SQLite database without mutating development databases:
```bash
# Run the complete test suite (259 automated tests)
.venv\Scripts\activate
python -m pytest -q

# Run frontend production build verification
cd frontend
npm run build
```

---

## 🔑 Demo Role Credentials

Default user accounts are initialized on startup. Passwords can be configured in your local `.env` configuration file using the variables below:

| Role | Username | Environment Variable (Configure in `.env`) | Privileges |
| :--- | :--- | :--- | :--- |
| 👑 **Administrator** | `admin` | `SENTINEL_ADMIN_PASSWORD` | Full System Control & Model Retraining |
| 🔬 **Security Analyst** | `analyst` | `SENTINEL_ANALYST_PASSWORD` | Traffic Inspection, Playbooks & Reports |
| 👁️ **Operations Viewer** | `viewer` | `SENTINEL_VIEWER_PASSWORD` | Read-Only Dashboard Monitoring |

---

## 📚 Complete Enterprise Documentation Suite

### 🚀 Guides & Operations
- 📖 [`docs/guides/CUSTOMER_QUICKSTART.md`](docs/guides/CUSTOMER_QUICKSTART.md) — 5-Minute Quickstart Guide for SOC Operators
- 👑 [`docs/guides/ADMIN_GUIDE.md`](docs/guides/ADMIN_GUIDE.md) — SOC Administrator & User Governance Manual
- 🔬 [`docs/guides/ANALYST_GUIDE.md`](docs/guides/ANALYST_GUIDE.md) — Tier 1/2/3 Security Analyst Operational Guide
- 🚀 [`docs/guides/DEPLOYMENT.md`](docs/guides/DEPLOYMENT.md) — Production Docker & Kubernetes Deployment Guide
- ⚙️ [`docs/guides/OPERATIONS.md`](docs/guides/OPERATIONS.md) — Operations Runbook & Model Governance Procedures
- 🔧 [`docs/guides/TROUBLESHOOTING.md`](docs/guides/TROUBLESHOOTING.md) — Diagnostics & Incident Resolution Manual
- 🤝 [`docs/guides/CONTRIBUTING.md`](docs/guides/CONTRIBUTING.md) — Developer & Contributor Standards

### 🏗️ Architecture, API & Security
- 🏗️ [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) — System Topology, Microservices & Data Flows
- 📖 [`docs/api/API.md`](docs/api/API.md) — REST API Endpoints & Real-time WebSocket Contracts
- 🛡️ [`docs/security/SECURITY.md`](docs/security/SECURITY.md) — Enterprise Security Hardening & RBAC Specifications
- 🎯 [`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md) — STRIDE Threat Model & MITRE ATT&CK Matrix

### 📊 Audits & Reports
- 🏆 [`docs/reports/AEGIVANTA_FINAL_PRODUCT_AUDIT.md`](docs/reports/AEGIVANTA_FINAL_PRODUCT_AUDIT.md) — Final Multi-Dimensional Product Audit
- 📋 [`docs/reports/AEGIVANTA_REPOSITORY_AUDIT.md`](docs/reports/AEGIVANTA_REPOSITORY_AUDIT.md) — Repository File Classification & Inventory

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <sub>Built with ❤️ for Enterprise SOC Operations. Aegivanta © 2026</sub>
</div>
