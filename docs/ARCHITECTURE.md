# SentinelAI — Architecture Overview

**Version**: 1.0.0 | **Last Updated**: 2026-08-13

---

## 1. System Overview

SentinelAI is a network intrusion detection and threat analytics platform. It consists of five integrated layers:

```
┌─────────────────────────────────────────────────────┐
│                  React SPA (Vite)                   │
│         SOC Dashboard / Predictions / Reports        │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────┐
│               FastAPI Backend (Python)               │
│   Auth │ RBAC │ Predict │ Analytics │ Train │ Incidents │
└──────┬─────────────────────────────┬────────────────┘
       │                             │
┌──────▼──────┐             ┌────────▼───────┐
│  SQLite /   │             │   ML Engine    │
│ PostgreSQL  │             │  (scikit-learn)│
│  (SQLAlchemy│             │  ml/artifacts/ │
│   Async)    │             └────────────────┘
└──────────────┘
```

---

## 2. Frontend Layer

- **Framework**: React 18 + TypeScript, Vite 5 bundler
- **Styling**: Tailwind CSS
- **State**: React Hooks (`useState`, `useEffect`, `useCallback`)
- **API Client**: Axios with `X-Request-ID` correlation header injection and 401 interceptor
- **Pages**: Dashboard, Predictions, Analytics, Model Registry, Incidents, Reports, Audit Logs
- **Real-time**: WebSocket subscription to `/ws/threat-stream`
- **Location**: `frontend/src/`

---

## 3. Backend Layer (FastAPI)

- **Framework**: FastAPI + Uvicorn ASGI
- **Database ORM**: SQLAlchemy 2.0 Async with `aiosqlite` / `asyncpg`
- **Authentication**: JWT Bearer tokens (HS256), 8-hour expiry
- **Authorization**: Role-based (`admin`, `analyst`, `viewer`)
- **Middleware**: `RequestTimingAndAuditMiddleware` — attaches `X-Request-ID`, measures latency, writes audit log
- **Location**: `backend/app/`

### API Routers
| Prefix | Module | Purpose |
|:---|:---|:---|
| `/health`, `/ready` | `api/v1/health.py` | Service health & readiness |
| `/api/v1/auth` | `api/v1/auth.py` | Login / token management |
| `/api/v1/users` | `api/v1/users.py` | User management (admin only) |
| `/api/v1/predict` | `api/v1/predict.py` | ML inference + XAI |
| `/api/v1/analytics` | `api/v1/analytics.py` | Summary / ROC / drift |
| `/api/v1/train` | `api/v1/train.py` | Training job trigger / promote / rollback |
| `/api/v1/incidents` | `api/v1/incidents.py` | Incident lifecycle management |
| `/api/v1/logs` | `api/v1/logs.py` | Audit log access |
| `/ws` | `api/v1/websockets.py` | Real-time threat stream |

---

## 4. ML Engine Layer

- **Location**: `ml/`
- **Dataset**: Synthetic CICIDS2017-schema data (`ml/dataset/generator.py`)
- **Preprocessing**: `CICIDS2017Preprocessor` — imputation, scaling, SelectKBest feature selection
- **Models**: Random Forest, XGBoost, LightGBM, CatBoost, Decision Tree, Logistic Regression, SVM, KNN, Naive Bayes, 1D-CNN (stub), LSTM (stub), Autoencoder (stub)
- **Artifacts**: Serialized via `joblib` in `ml/artifacts/`
- **Explainability**: SHAP TreeExplainer for tree models (`ml/explainability/real_explainer.py`)
- **Drift Detection**: PSI + KS-test sliding window monitor (`ml/monitoring/drift_detector.py`)

---

## 5. Database Layer

- **Schema tables**: `User`, `Incident`, `ModelRegistry`, `AuditLog`, `TrainingJob`
- **Development**: SQLite (`sentinelai.db`)
- **Production**: PostgreSQL 16 via asyncpg
- **Migrations**: Managed via `backend/app/database.py` (`create_all` on startup)

---

## 6. Container Architecture (Docker)

```
sentinel_frontend (nginx:1.27-alpine)
       │ proxy_pass /api/ → backend:8000
sentinel_backend (python:3.11-slim, user: sentinelai:1001)
       │ depends_on: postgres (healthy), redis (healthy)
sentinel_postgres (postgres:16-alpine)
sentinel_redis    (redis:7-alpine)
```

All services on isolated `sentinel_net` bridge network. PostgreSQL and Redis not exposed publicly.

---

## 7. Security Architecture

- JWT HS256 tokens with configurable expiry
- Bcrypt password hashing (via `passlib`)
- RBAC enforcement at router level (`Depends(require_role(...))`)
- CORS restricted to configured origins
- Production fail-closed: `validate_production_settings()` raises `RuntimeError` on startup if secrets missing
- Audit logging on all mutating operations via middleware
- Operating modes: `DEMO`, `LAB`, `PRODUCTION`
