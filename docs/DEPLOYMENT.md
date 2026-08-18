# SentinelAI — Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2026-08-13  

---

## 1. Prerequisites

| Requirement | Minimum Version |
|:---|:---|
| Python | 3.11 |
| Node.js | 20.x LTS |
| npm | 9.x |
| Docker | 24.x (optional) |
| Docker Compose | 2.x (optional) |
| Git | 2.x |

---

## 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/ANURAG20042006/SENTINELAI.git
cd SENTINELAI

# Copy environment template
cp .env.example .env

# Edit .env with your actual values
# REQUIRED fields:
#   SECRET_KEY           — at least 32 character random hex string
#   POSTGRES_PASSWORD    — strong database password (production only)
#   SENTINEL_ADMIN_PASSWORD
#   SENTINEL_ANALYST_PASSWORD
#   SENTINEL_VIEWER_PASSWORD
```

Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. Database Setup

### Option A — SQLite (Development / Demo)
SQLite is used by default and requires no additional setup. The database file `sentinelai.db` is created automatically on first startup.

```ini
DATABASE_URL=sqlite+aiosqlite:///./sentinelai.db
```

### Option B — PostgreSQL (Production)
```ini
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@localhost:5432/sentinelai_db
POSTGRES_USER=sentinel_admin
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=sentinelai_db
```

---

## 4. ML Artifact Generation

The backend requires trained ML artifacts to make predictions. Generate them by running the training pipeline:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the full training pipeline
python -m ml.train_pipeline

# Verify artifacts were created
ls ml/artifacts/
# Expected: best_model.joblib, preprocessor.joblib, metadata.json, artifact_manifest.json
```

> **Note**: The training pipeline uses a synthetic CICIDS2017-schema dataset. For production use, replace `ml/dataset/generator.py` with a loader for the real CICIDS2017 dataset.

---

## 5. Backend Startup (Local)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI backend (development)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Access API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc:      http://localhost:8000/redoc
# Health:     http://localhost:8000/health
# Readiness:  http://localhost:8000/ready
```

---

## 6. Frontend Startup (Local)

```bash
cd frontend
npm install
npm run dev
# Access: http://localhost:5173
```

---

## 7. Docker Compose Startup

### 7.1 Set required environment variables
```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export POSTGRES_PASSWORD=<strong-db-password>
export SENTINEL_ADMIN_PASSWORD=<admin-password>
export SENTINEL_ANALYST_PASSWORD=<analyst-password>
export SENTINEL_VIEWER_PASSWORD=<viewer-password>
```

Or add them to a `.env` file in the project root.

### 7.2 Validate the compose configuration
```bash
docker compose -f docker/docker-compose.yml config
```

### 7.3 Build and start all services
```bash
docker compose -f docker/docker-compose.yml up --build -d
```

### 7.4 Verify service health
```bash
docker compose -f docker/docker-compose.yml ps
curl http://localhost/health
curl http://localhost/ready
```

### 7.5 View logs
```bash
docker compose -f docker/docker-compose.yml logs -f backend
```

### 7.6 Stop all services
```bash
docker compose -f docker/docker-compose.yml down
```

---

## 8. Operating Modes

| Mode | Description | Production Secrets Required |
|:---|:---|:---|
| `DEMO` | Development/demo mode — dev password fallbacks active | No |
| `LAB` | Research mode — training and experiments enabled | No |
| `PRODUCTION` | Full enforcement — all env vars required, localhost CORS rejected | Yes |

Set via `.env`:
```ini
OPERATING_MODE=PRODUCTION
APP_ENV=production
```

---

## 9. Seeded User Accounts

User passwords MUST be provided via environment variables on initial startup:

| Username | Role | Required Environment Variable |
|:---|:---|:---|
| `admin` | admin | `SENTINEL_ADMIN_PASSWORD` |
| `analyst` | analyst | `SENTINEL_ANALYST_PASSWORD` |
| `viewer` | viewer | `SENTINEL_VIEWER_PASSWORD` |

> **Security Enforcement**: SentinelAI does not embed hardcoded fallback user passwords in application source code. Application startup will fail closed with a `RuntimeError` if these environment variables are missing.

---

## 10. Production Checklist

- [ ] Generate unique `SECRET_KEY` (min 32 chars)
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Set `SENTINEL_*_PASSWORD` for all seeded users
- [ ] Set `OPERATING_MODE=PRODUCTION`
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` with specific frontend origins (no wildcards, no localhost)
- [ ] Run ML training pipeline to generate artifacts before backend startup
- [ ] Verify `/health` and `/ready` endpoints respond correctly
- [ ] Ensure no secrets are committed to version control
