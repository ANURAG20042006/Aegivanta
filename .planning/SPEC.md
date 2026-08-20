# Aegivanta Architectural & Technical Specification

## 1. System Invariants
- **Backend**: FastAPI running on Python 3.11 with asynchronous route handlers and strict Pydantic v2 schemas.
- **Machine Learning**: Scikit-Learn 1.6.1 pinned authoritatively. Model champion: CatBoost with TreeSHAP feature explanations.
- **SOAR Security Policy**: Strictly zero shell/eval execution. Remediations (`BLOCK_IP`, `ISOLATE_HOST`, `QUARANTINE_ASSET`, `REVOKE_SESSION`, `DISABLE_ACCOUNT`) must execute through deterministic provider abstractions with rollback journaling.
- **Data Stores**: PostgreSQL 15+ for relational audit/state, Redis for IOC cache / sliding window correlation, SQLite supported in single-node demo mode.
- **Frontend**: TypeScript, React 18, Vite, Tailwind CSS, Lucide icons, Recharts for visual analytics.

## 2. Agent Execution Constraints
- Every code modification must satisfy `scikit-learn==1.6.1` environment checks.
- All database mutations must use transactional boundaries with migration parity.
- Security-critical endpoints must require JWT Bearer authentication and RBAC roles (`admin`, `analyst`, `viewer`).
- No secrets or credentials may be hardcoded. Environment variables must be loaded through validated settings.

## 3. Verification Protocol
1. Environment verification: `scripts/verify_environment.py`
2. Test suite: `pytest -q`
3. Artifact integrity: `scripts/final_integrity_audit.py`
4. Kubernetes manifests: `scripts/validate_k8s_manifests.py`
