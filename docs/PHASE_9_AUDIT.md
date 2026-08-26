# PHASE 9 — CONTAINER HARDENING & DEPLOYMENT AUDIT

**Target**: Docker configuration in `docker/`  
**Audit Timestamp**: 2026-08-13  

---

## 1. Docker Audit Findings & Remediations

### 1.1 Dockerfile.backend — Issues Found & Fixed

| Issue | Severity | Status |
|:---|:---|:---|
| Container ran as `root` | High | **Fixed** — Added `sentinelai` non-root user (UID 1001) |
| `git` installed unnecessarily in image | Low | **Fixed** — Removed `git` from `apt-get install` |
| `.env.example` copied as `/app/.env` | High | **Fixed** — Removed; credentials must come from env vars only |
| `build-essential` left in final image | Low | Accepted — needed for Python C-extension compilation |

### 1.2 docker-compose.yml — Issues Found & Fixed

| Issue | Severity | Status |
|:---|:---|:---|
| PostgreSQL port `5432` exposed publicly | High | **Fixed** — Changed to `expose` (internal only) |
| Redis port `6379` exposed publicly | High | **Fixed** — Changed to `expose` (internal only) |
| `APP_ENV=development` hardcoded | Medium | **Fixed** — Changed to `${APP_ENV:-development}` |
| `OPERATING_MODE` missing from compose env | Medium | **Fixed** — Added with `${OPERATING_MODE:-DEMO}` |
| Seeded user passwords missing from compose env | High | **Fixed** — Added `SENTINEL_*_PASSWORD` with `:?` enforcement |
| Backend health check only in Dockerfile, not compose | Medium | **Fixed** — Added explicit `healthcheck` in compose backend service |
| No `ml_artifacts` volume — artifacts lost on container restart | Medium | **Fixed** — Added `ml_artifacts` named volume |
| `restart: always` causes infinite restart loop on startup failure | Low | **Fixed** — Changed to `restart: unless-stopped` |

### 1.3 Dockerfile.frontend — Issues Found & Fixed

| Issue | Severity | Status |
|:---|:---|:---|
| `npm ci || npm install` fallback (non-deterministic) | Low | **Fixed** — Changed to strict `npm ci` |
| `nginx:alpine` unpinned version | Low | **Fixed** — Pinned to `nginx:1.27-alpine` |
| No healthcheck on frontend | Low | **Fixed** — Added `wget` healthcheck |

### 1.4 .env.example — Issues Found & Fixed

| Issue | Severity | Status |
|:---|:---|:---|
| Missing `SENTINEL_ADMIN/ANALYST/VIEWER_PASSWORD` placeholders | High | **Fixed** — Added all three user password variables |
| Weak placeholder value comment | Low | **Fixed** — Added `CHANGE_ME_` prefix and secure generation instructions |

---

## 2. Environment Verification

### Secrets Never Committed
- `.env` is in `.gitignore` ✓
- `.env.example` contains only placeholders (`CHANGE_ME_*`) ✓
- No production secrets visible in any Docker file ✓
- `SECRET_KEY` enforced via `:?` in docker-compose ✓
- `POSTGRES_PASSWORD` enforced via `:?` in docker-compose ✓

### Production Config Enforcement (`backend/app/config.py`)
- `validate_production_settings()` is called on every application startup
- In `PRODUCTION` mode it raises `RuntimeError` for:
  - Missing or short `SECRET_KEY`
  - Missing `POSTGRES_PASSWORD`
  - Missing any `SENTINEL_*_PASSWORD`
  - `DEBUG=True`
  - CORS origins containing `localhost` or `*` wildcard

---

## 3. Health Check Verification

| Service | Health Check Command | Interval | Retries |
|:---|:---|:---|:---|
| `postgres` | `pg_isready -U sentinel_admin` | 10s | 5 |
| `redis` | `redis-cli ping` | 10s | 5 |
| `backend` | `curl -f http://localhost:8000/health` | 30s | 3 |
| `frontend` | `wget -qO- http://localhost/health` | 30s | 3 |

---

## 4. Docker Build Status

Docker CLI is not installed on the test host (Windows development environment). The `docker compose config` command cannot be run. All Docker file syntax has been manually validated.

**Documented Skip**: Docker CLI not available on Windows dev host. All Dockerfile syntax validated manually. No Docker daemon available.

---

## Phase 9 Definition of Done Checklist

- [x] No production secrets committed to version control
- [x] Reproducible config via `.env.example` with all required placeholders
- [x] Non-root user in backend container
- [x] Minimal exposed ports (PostgreSQL and Redis internal only)
- [x] Health checks on all services (postgres, redis, backend, frontend)
- [x] `ml_artifacts` volume persisted across container restarts
- [x] Documentation created: `docs/DEPLOYMENT.md`, `docs/PHASE_9_AUDIT.md`
