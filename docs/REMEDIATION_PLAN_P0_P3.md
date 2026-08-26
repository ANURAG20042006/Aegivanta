# AEGIVANTA — REMEDIATION PLAN (P0–P3 PRIORITY TIERS)

**Audit Date:** August 21, 2026  
**Auditor:** Principal DevSecOps & Production Architect  
**Classification:** STRUCTURED REMEDIATION ROADMAP  

---

> [!NOTE]  
> This remediation plan is the **output of the read-only audit**. No source code was modified.  
> Items are classified P0–P3 based on blast radius and production impact.

---

## Priority Classification

| Priority | Description | SLA to Resolve |
| :--- | :--- | :--- |
| **P0** | Critical blocker; prevents production deployment | Immediate |
| **P1** | High priority; degrades security or reliability | Within 1 week |
| **P2** | Medium; increases technical debt or operational risk | Within 1 month |
| **P3** | Low; quality improvements and nice-to-haves | Backlog |

---

## P0 — Critical Blockers

**Status: NONE FOUND ✅**

No P0 blockers were identified. The codebase contains no plaintext secrets, no authentication bypass paths, no SQL injection vectors, and no critical data corruption risks.

---

## P1 — High Priority (Resolve Within 1 Week)

### P1-001: SQLite → PostgreSQL for Production Concurrency
- **Description**: The current default `DATABASE_URL` uses SQLite via `aiosqlite`. SQLite cannot support concurrent multi-process writes required for production load under multiple Uvicorn/Gunicorn workers or multi-pod Kubernetes deployments.
- **Risk**: Write contention, table locking, and `database is locked` errors under concurrent load.
- **Resolution**: Set `DATABASE_URL=postgresql+asyncpg://user:password@host/dbname` in production `.env`.
- **Files**: `backend/app/config.py`, `.env` (production environment).

### P1-002: Redis Required for Rate Limiting, Streams & Caching
- **Description**: Several services, including distributed stream consumers (`distributed_stream_service.py`) and rate limiting (`core/rate_limit.py`), attempt Redis connections. If Redis is unavailable, workers fail silently or use degraded in-memory fallbacks.
- **Risk**: Rate limiting bypass, message queue loss, cross-instance session data inconsistency.
- **Resolution**: Deploy Redis 7+ cluster and set `REDIS_URL=redis://...` in the production environment.
- **Files**: `backend/app/config.py`, `k8s/redis.yaml`.

---

## P2 — Medium Priority (Resolve Within 1 Month)

### P2-001: Frontend Bundle Size Optimization
- **Description**: The production JavaScript bundle is `1,364 KB` (290 KB gzipped). Vite warns that chunks exceed the 500 KB limit.
- **Risk**: Slower initial load time on low-bandwidth connections.
- **Resolution**: Implement React lazy-loading (`React.lazy`) and dynamic `import()` splits for major page groups in `frontend/src/App.tsx`.
- **Files**: `frontend/src/App.tsx`, `frontend/vite.config.ts`.

### P2-002: Formal Database Migration Tool (Alembic)
- **Description**: Schema evolution is handled via inline `ALTER TABLE ADD COLUMN` statements inside `database.py`. This is non-standard; `alembic` is installed but unused.
- **Risk**: Difficult rollbacks, missing down-migration paths, and audit trail gaps for schema changes.
- **Resolution**: Initialize Alembic migration directory; convert existing column additions to versioned migration files.
- **Files**: `backend/app/database.py`, create `alembic/` migrations directory.

### P2-003: Structured Async Logging Instead of Print
- **Description**: Several services use `logger.info(f"...")` f-string formatting rather than `logger.info("%s", val)` lazy %-formatting, which evaluates the string even when logging is disabled.
- **Risk**: Minor performance overhead at scale.
- **Resolution**: Replace f-string logger calls with positional argument format across services.

### P2-004: Deep Learning Model Artifacts (LSTM, Autoencoder, 1D-CNN)
- **Description**: Three neural model artifacts (`lstm.joblib`, `autoencoder.joblib`, `1d-cnn.joblib`) are 4-byte placeholder files. They return `None` probabilities and are excluded from the prediction ensemble.
- **Risk**: Documentation accuracy gap; claiming 9-model ensemble when 3 are stubs.
- **Resolution**: Train and serialize real LSTM/Autoencoder implementations or remove them from the model registry manifest.
- **Files**: `ml/artifacts/`, `ml/train_pipeline.py`, `ml/artifacts/metadata.json`.

---

## P3 — Low Priority (Backlog)

### P3-001: API Response Schema Consistency for Postured Services
- **Description**: Some posture services return raw Python dicts rather than typed Pydantic response models.
- **Resolution**: Formalize Pydantic response schemas for all posture service endpoints.

### P3-002: WebSocket Hub Reconnection & Back-Pressure
- **Description**: The WebSocket hub (`websockets.py`) does not implement exponential back-off reconnection or back-pressure signals for slow consumers.
- **Resolution**: Add heartbeat timeout, client buffer limits, and reconnection signaling.

### P3-003: Test Coverage for Frontend React Components
- **Description**: The frontend has 0 unit tests (no Vitest/Jest test files exist in `frontend/src/`). All testing is done via backend unit and integration tests.
- **Resolution**: Add React Testing Library component tests for critical UI flows (Login, Alert Queue, SOC Dashboard).

### P3-004: OpenAPI Spec Export & Contract Testing
- **Description**: The FastAPI `/openapi.json` spec is generated dynamically but not committed to the repository for external contract testing.
- **Resolution**: Add a CI step to export and commit `openapi.json` on every release, enabling consumer-driven contract testing.

---

## Summary: Remediation Priority Count

| Priority | Count | Status |
| :--- | :--- | :--- |
| **P0 Critical** | 0 | ✅ None |
| **P1 High** | 2 | ⚠️ Requires Infrastructure Configuration |
| **P2 Medium** | 4 | 🔶 Technical Debt & Quality Improvements |
| **P3 Low** | 4 | 📋 Backlog Enhancements |
