# AEGIVANTA — COMPREHENSIVE REPOSITORY AUDIT

**Product**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Repository**: [https://github.com/ANURAG20042006/SENTINELAI](https://github.com/ANURAG20042006/SENTINELAI)  
**Date**: 2026-08-20  
**Audit Purpose**: Complete repository inspection, classification of every artifact, identification of production assets vs. development-only artifacts, security review, and clean release roadmap.

---

## 1. Executive Summary & Inventory Overview

| Category | Item Count | Status / Health | Description |
|---|:---:|:---:|---|
| **Backend Core & APIs** | 35 Modules | 🟢 PRODUCTION REQUIRED | FastAPI gateway, async SQLAlchemy, JWT Auth, RBAC, Rate Limiting, Threat Intel, SOAR, Hunting, Graph Analytics, WebSockets. |
| **Machine Learning Engine** | 12 Models | 🟢 PRODUCTION REQUIRED | Preprocessor pipelines, CatBoost champion model, SHAP explainers, drift detectors, reproducible feature schema. |
| **Frontend Commercial UI** | 22 Pages/Views | 🟢 PRODUCTION REQUIRED | React 18, TypeScript, Tailwind CSS, Lucide icons, Dark SOC styling, live telemetry streams, attack topology. |
| **Distributed Infrastructure** | 18 Manifests | 🟢 PRODUCTION REQUIRED | Kubernetes deployments, non-root UID 10001 hardening, HPA, PDB, NetworkPolicies, Redis Streams backend + DLQ. |
| **Test Suite** | 560+ Test Cases | 🟢 PRODUCTION REQUIRED | Unit, integration, e2e, security RBAC, ML inference, DLQ, and benchmark validation tests. |
| **Operational Documentation** | 12 Guides | 🟢 PRODUCTION REQUIRED | Production readiness, disaster recovery, runbooks, architecture, threat model, API contracts. |
| **Historical Phase Reports** | 28 Files | 🟡 ARCHIVE / REFERENCE | Historical phase validation logs (Phase 0 through Phase 3.15) preserved for audit provenance. |

---

## 2. Granular Component Classification

### A. Backend (`backend/`)
| File / Directory | Classification | Rationale & Status |
|---|---|---|
| `backend/app/main.py` | `PRODUCTION REQUIRED` | Application gateway entrypoint, lifespan manager, user initialization, exception filters. |
| `backend/app/config.py` | `PRODUCTION REQUIRED` | Pydantic v2 settings, fail-closed production credential validators, environment variables. |
| `backend/app/database.py` | `PRODUCTION REQUIRED` | Async SQLAlchemy engine, NullPool for test isolation, session generators. |
| `backend/app/security.py` | `PRODUCTION REQUIRED` | Argon2/Bcrypt password hashing, JWT token encoding/decoding, RBAC role claims. |
| `backend/app/api/v1/auth.py` | `PRODUCTION REQUIRED` | JWT login, password rotation, profile retrieval. |
| `backend/app/api/v1/telemetry.py`| `PRODUCTION REQUIRED` | Telemetry ingestion, PCAP upload, streaming dispatch. |
| `backend/app/api/v1/predict.py` | `PRODUCTION REQUIRED` | Single & batch ML threat inference with SHAP explanations. |
| `backend/app/api/v1/alerts.py` | `PRODUCTION REQUIRED` | Live threat alert feed, multi-state triage lifecycle. |
| `backend/app/api/v1/incidents.py`| `PRODUCTION REQUIRED` | Incident ledger, severity escalation, evidence attachment. |
| `backend/app/api/v1/threat_intel.py`| `PRODUCTION REQUIRED` | IOC database, threat feed synchronization, fast cache. |
| `backend/app/api/v1/threat_graph.py`| `PRODUCTION REQUIRED` | Multi-hop lateral movement graph, blast-radius calculation. |
| `backend/app/api/v1/hunting.py` | `PRODUCTION REQUIRED` | Threat hunting engine, hypothesize-and-test queries. |
| `backend/app/api/v1/investigations.py`| `PRODUCTION REQUIRED` | Security investigation case management and evidence graph. |
| `backend/app/api/v1/response.py` | `PRODUCTION REQUIRED` | Autonomous SOAR playbooks, dry-run simulation, rollback engine. |
| `backend/app/api/v1/adaptive_ml.py`| `PRODUCTION REQUIRED` | Adaptive learning, drift monitoring, champion-challenger registry. |
| `backend/app/api/v1/health.py` | `PRODUCTION REQUIRED` | Liveness, readiness, and Prometheus metrics endpoints. |
| `backend/app/services/*` | `PRODUCTION REQUIRED` | Core business logic services (SOAR, correlation, graph, ML, PCAP, Redis Streams). |
| `backend/app/models/*` | `PRODUCTION REQUIRED` | SQLAlchemy relational database models with foreign keys and indexes. |

### B. Machine Learning Engine (`ml/`)
| File / Directory | Classification | Rationale & Status |
|---|---|---|
| `ml/artifacts/best_model.joblib` | `PRODUCTION REQUIRED` | Authoritative CatBoost champion model artifact. |
| `ml/artifacts/preprocessor.joblib` | `PRODUCTION REQUIRED` | Scikit-learn 1.6.1 preprocessor and feature scaler. |
| `ml/artifacts/metadata.json` | `PRODUCTION REQUIRED` | Non-fabricated training provenance and CV benchmark metrics. |
| `ml/artifacts/artifact_manifest.json`| `PRODUCTION REQUIRED` | SHA-256 integrity verification manifest. |
| `ml/schema/feature_schema.py` | `PRODUCTION REQUIRED` | Strict 30-feature CICIDS2017 schema definition and validation. |
| `ml/src/train.py` | `DEVELOPMENT ONLY` | Pipeline script for offline model retraining. |
| `ml/src/evaluate.py` | `DEVELOPMENT ONLY` | Pipeline script for evaluating offline candidate models. |

### C. Frontend (`frontend/`)
| File / Directory | Classification | Rationale & Status |
|---|---|---|
| `frontend/src/App.tsx` | `PRODUCTION REQUIRED` | Full-width application layout, routing, and WebSocket context provider. |
| `frontend/src/pages/Dashboard.tsx` | `PRODUCTION REQUIRED` | SOC Command Center dashboard with metric ribbons, live streams, and widgets. |
| `frontend/src/pages/Login.tsx` | `PRODUCTION REQUIRED` | Secure login interface with demo role auto-fill and validation. |
| `frontend/src/pages/ThreatHunting.tsx`| `PRODUCTION REQUIRED` | Interactive threat hunting and entity query workspace. |
| `frontend/src/pages/ThreatGraph.tsx`| `PRODUCTION REQUIRED` | Interactive attack topology visualization. |
| `frontend/src/pages/InvestigationsView.tsx`| `PRODUCTION REQUIRED`| Investigation case ledger and evidence timeline. |
| `frontend/src/pages/ResponseCenter.tsx`| `PRODUCTION REQUIRED`| SOAR action approval and execution center. |
| `frontend/src/components/*` | `PRODUCTION REQUIRED` | Modular charts, tables, ribbons, and modals (all imported and verified). |

### D. Distributed Deployment (`k8s/`, `docker/`)
| File / Directory | Classification | Rationale & Status |
|---|---|---|
| `k8s/deployment-api.yaml` | `PRODUCTION REQUIRED` | 3-replica API deployment with dropped capabilities and non-root UID 10001. |
| `k8s/deployment-worker.yaml` | `PRODUCTION REQUIRED` | Dedicated stream worker daemon deployment. |
| `k8s/redis.yaml` | `PRODUCTION REQUIRED` | Redis StatefulSet with password protection and internal networking. |
| `k8s/networkpolicy.yaml` | `PRODUCTION REQUIRED` | Strict microsegmentation policy (DNS 53, Redis 6379, DB 5432). |
| `k8s/hpa.yaml`, `k8s/pdb.yaml` | `PRODUCTION REQUIRED` | Horizontal Pod Autoscaler and Pod Disruption Budget. |
| `docker/docker-compose.yml` | `PRODUCTION REQUIRED` | Multi-container stack (backend, frontend, postgres, redis). |
| `docker/Dockerfile.backend` | `PRODUCTION REQUIRED` | Multi-stage hardened backend container build. |

### E. Tests (`tests/`)
| Directory / File | Classification | Rationale & Status |
|---|---|---|
| `tests/unit/*` | `PRODUCTION REQUIRED` | Unit tests for SOAR, correlation, graph analytics, DLQ, adaptive ML. |
| `tests/integration/*` | `PRODUCTION REQUIRED` | End-to-end multi-step SOC pipeline integration tests. |
| `tests/api/*` | `PRODUCTION REQUIRED` | REST API route contracts, payload validation, and status code checks. |
| `tests/security/*` | `PRODUCTION REQUIRED` | JWT revocation, RBAC privilege escalation prevention, SSRF defense tests. |
| `tests/ml/*` | `PRODUCTION REQUIRED` | Feature schema validation, SHAP explainability, and artifact hash integrity. |

---

## 3. Security & Quality Findings Summary

1. **Authentication & RBAC**: Strict JWT with SHA256 signature verification. Public registration is locked to the `viewer` role only.
2. **SOAR Remediation Safety**: Zero sub-process / shell execution. All actions (`BLOCK_IP`, `ISOLATE_HOST`, etc.) use structured internal state transitions, dry-run simulation mode, and complete rollback history.
3. **Fail-Closed Design**: Production environment validator enforces strong 32+ character secrets and non-empty database/seed passwords.
4. **Memory & Thread Safety**: SQLite asynchronous connections enforce `NullPool` to eliminate connection worker leaks. OpenMP is constrained to 1 thread on Linux runners to guarantee deterministic execution without core dumps.

---

## 4. Remediation & Action Plan

- **Keep**: All active backend, frontend, ML, Docker, Kubernetes, and test code.
- **Maintain**: Backward-compatible aliases for legacy environment variables and exceptions (`SENTINEL_*` → `AEGIVANTA_*`).
- **Standardize**: Product description across all documentation as `"Aegivanta — Autonomous Cyber Defense & Security Operations Platform"`.
