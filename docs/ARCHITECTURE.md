# SentinelAI System Architecture Document

## Executive Overview
SentinelAI is an enterprise-grade Network Intrusion Detection System (NIDS) and Threat Analytics Platform designed to detect cyber threats in real time using Machine Learning and Deep Learning. The architecture follows modern microservice-ready modular monolith design patterns, adhering strictly to **SOLID design principles**, **Clean Architecture**, and **Domain-Driven Design (DDD)** principles.

---

## 1. High-Level Architectural Layers

```
                                  +---------------------------------------+
                                  |     React 18 SPA (Vite / TS / MUI)    |
                                  |   Framer Motion / Chart.js / Tailwind |
                                  +-------------------+-------------------+
                                                      |
                                       HTTPS / REST   |   WebSockets (WSS)
                                                      v
                                  +-------------------+-------------------+
                                  |        FastAPI ASGI Application       |
                                  |     (Authentication / WebSockets)     |
                                  +---------+-------------------+---------+
                                            |                   |
                     +----------------------+                   +----------------------+
                     |                                                                 |
                     v                                                                 v
+--------------------+--------------------+                         +------------------+------------------+
|           Database Layer               |                         |         Machine Learning Engine          |
|  PostgreSQL 16 Async + Redis 7 Cache   |                         |   12 Models (Scikit-Learn, PyTorch,  |
|  SQLAlchemy 2.0 ORM + Alembic Schema   |                         |   XGBoost, CatBoost, LightGBM, SHAP) |
+-----------------------------------------+                         +-------------------------------------+
```

---

## 2. Technology Stack Matrix

| Layer | Primary Technology | Supporting Frameworks / Libraries |
| :--- | :--- | :--- |
| **Frontend Framework** | React 18 (Vite SPA) | TypeScript 5.2, React Router v6 |
| **Styling & Design** | Tailwind CSS v3 | Material UI (MUI v5), Lucide Icons |
| **Data Visualization** | Chart.js & react-chartjs-2 | Custom Canvas Heatmaps & ROC Curves |
| **Animations** | Framer Motion v11 | CSS Grid Cyberpunk Keyframes |
| **Backend API** | Python 3.11+ / FastAPI | Pydantic v2, Uvicorn ASGI Server |
| **Authentication** | OAuth2 with JWT | Passlib (Bcrypt), Python-Jose |
| **Real-time Protocol**| Native FastAPI WebSockets | Custom ConnectionManager Broadcast Pool |
| **Database ORM** | Async SQLAlchemy 2.0 | Asyncpg Driver, Alembic Migrations |
| **Database Engine** | PostgreSQL 16 | Redis 7 (Caching & Rate Limiting) |
| **ML Models (12)** | Scikit-Learn, XGBoost | LightGBM, CatBoost, PyTorch |
| **Explainable AI** | SHAP | LIME |
| **Report Generation** | ReportLab (PDF) | OpenPyXL (Excel), Python CSV |
| **Containerization** | Docker | Docker Compose, GitHub Actions CI/CD |

---

## 3. Core Design Patterns & SOLID Principles

### A. Single Responsibility Principle (SRP)
- **Database ORM Models** define data attributes only.
- **Pydantic Schemas** handle serialization and validation rules.
- **Service Modules** handle business logic execution.
- **API Routers** map HTTP verbs and status codes to service responses.

### B. Open/Closed Principle (OCP)
- **Base ML Model Strategy (`base_model.py`)**: Abstract base class defining `fit()`, `predict()`, and `predict_proba()`. New models can be added without modifying the ingestion framework.

### C. Dependency Inversion Principle (DIP)
- FastAPI endpoints depend on abstract repository interfaces passed via `Depends()` dependency injection rather than concrete database connections.

### D. Repository & Unit of Work Pattern
- Data retrieval logic is encapsulated inside repository services (`UserRepository`, `IncidentRepository`), insulating business logic from storage choices.

---

## 4. Cyber Threat Classification Taxonomy (CICIDS2017 Benchmark)

SentinelAI categorizes network flows into 15 distinct classes:
1. **BENIGN**: Normal operational network flows.
2. **DDoS**: Distributed Denial of Service (UDP, TCP, HTTP flood).
3. **DoS**: Denial of Service (Slowloris, Slowhttptest, Hulk, GoldenEye).
4. **Port Scan**: Reconnaissance scans (Nmap, SYN scan, FIN scan).
5. **Botnet**: Command & Control (C2) bot network traffic.
6. **SQL Injection**: Database vulnerability exploitation payloads.
7. **XSS**: Cross-Site Scripting attack vectors in HTTP streams.
8. **Brute Force**: Automated credential stuffing (FTP-Patator, SSH-Patator).
9. **MITM**: Man-In-The-Middle packet interception.
10. **ARP Spoofing**: Address Resolution Protocol cache poisoning.
11. **DNS Spoofing**: Cache poisoning & DNS redirection attacks.
12. **Ransomware**: File encryption payload transfer and C2 beaconing.
13. **Malware**: Malicious code transfer and execution indicators.
14. **Data Exfiltration**: Covert channel data extraction over unexpected ports.
15. **Zero-Day Anomaly**: Unsupervised Autoencoder flagged anomalous flows.
