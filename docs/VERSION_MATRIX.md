# Aegivanta Platform — Version Matrix

**Status**: Authoritative Version Source of Truth  
**Last Audit**: August 2026  

---

## 📋 Component Version Inventory

| Component | Version | Source of Truth | Notes |
|:---|:---|:---|:---|
| **Platform / Product Release** | `v50.0.0` | `frontend/package.json`, `backend/app/config.py` | Unified capstone platform release |
| **Backend Service (FastAPI)** | `50.0.0` | `backend/app/main.py`, `backend/app/config.py` | FastAPI Application Version |
| **Frontend UI (React / Vite)** | `50.0.0` | `frontend/package.json` | React 18.2 / Vite 5.1 / TypeScript 5.2 |
| **Champion ML Model** | `catboost-v1.0` | `ml/artifacts/metadata.json`, `ml/artifacts/provenance.json` | CatBoost intrusion classifier |
| **Feature Schema** | `schema-v1.0` | `ml/schema/feature_schema.py` | 78 raw -> 30 selected features |
| **ML Experiment** | `EXP-2026-002` | `results/EXP-2026-002/experiment_manifest.json` | 5,000 synthetic benchmark dataset |
| **Historical Experiment** | `EXP-2026-001` | `results/archive/EXP-2026-001/` | Historical research baseline |
| **Python Runtime** | `3.11.5` | `.python-version`, `ml/artifacts/metadata.json` | CPython runtime environment |
| **Node.js Environment** | `20+` | `frontend/package.json` engines | LTS Node.js runtime |
| **Docker Compose Services** | `3.8` | `docker-compose.yml` | Multi-container microservices spec |
| **Database Schema** | `v50.0.0` | `backend/app/database.py`, `sentinelai.db` | SQLite / PostgreSQL relational schema |
| **API Contract** | `v1` (`/api/v1`) | `backend/app/config.py:API_V1_STR` | REST & WebSocket API specification |
