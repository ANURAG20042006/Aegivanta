# SENTINELAI — PHASE 3.3 PRODUCTION KUBERNETES & DEPLOYMENT HARDENING AUDIT
=============================================================================

## 1. Executive Summary & Baseline State

- **Target System**: SentinelAI — Production AI Network Intrusion Detection & SOC Platform
- **Frozen Baselines**:
  - Phase 1 Baseline: 266 passed / 0 failed / 17 skipped (Commit: `6d523e0`, Tag: `phase-1-verified`)
  - Phase 2 Baseline: 274 passed / 0 failed / 17 skipped (Commit: `0115bbb`)
  - Phase 3.1 Baseline: 284 passed / 0 failed / 17 skipped (Commit: `b19797f`)
  - Phase 3.2 Baseline: 295 passed / 0 failed / 17 skipped (Commit: `e74d979`)
- **Objective**: Harden deployment infrastructure and author production Kubernetes manifests with zero degradation to existing ML, SOC, PCAP, and Redis Streams streaming pipelines.

---

## 2. Existing Deployment Assumptions & Gap Analysis

| Dimension | Existing Docker / Compose State | Target Production Kubernetes Topology | Risk / Mitigation |
| :--- | :--- | :--- | :--- |
| **Execution User** | Non-root `sentinelai` (UID 1001) | Hardened `securityContext` (`runAsNonRoot: true`, `runAsUser: 10001`, `runAsGroup: 10001`) | P0: Enforce in all PodSpecs |
| **Privileges & Caps** | Default Docker capabilities | `allowPrivilegeEscalation: false`, `capabilities: { drop: ["ALL"] }`, `seccompProfile: RuntimeDefault` | P0: Zero root/escalation risks |
| **Filesystem State** | Writable root container filesystem | `readOnlyRootFilesystem: true` with ephemeral `emptyDir` mounts for `/tmp` and `/app/logs` | P1: Immutable container image |
| **API & Worker Topology** | Single monolithic backend container | Independent **API Deployments** (stateless HTTP/WS) and **Worker Deployments** (Redis stream consumers) | P0: Prevent duplicate processing |
| **Autoscaling** | Static container count | Kubernetes **HPA** (Horizontal Pod Autoscaler) targeting 70% CPU / 80% Memory | P1: Independent scale targets |
| **Availability & Disruption** | Docker `restart: unless-stopped` | **PodDisruptionBudget (PDB)** ensuring minimum 1 available replica during node drains | P1: Zero downtime updates |
| **Network Isolation** | Single bridge network `sentinel_net` | Kubernetes **NetworkPolicy** restricting API/Worker ingress/egress to Redis & PostgreSQL | P0: Defense-in-depth isolation |
| **Secrets Management** | Plaintext `.env` / compose env | Kubernetes **Secret** templates decoupled from **ConfigMap** (zero credentials committed) | P0: Secret scanning compliance |
| **Ingress & TLS** | Static Nginx proxy | Kubernetes **Ingress** with TLS termination, WebSocket upgrades, and secure headers | P1: TLS 1.3 encryption |

---

## 3. Dedicated Telemetry Privilege Isolation (`CAP_NET_RAW`)
- **Critical Policy**: The primary `sentinelai-api` and `sentinelai-worker` pods will **NEVER** run with `CAP_NET_RAW` or root privileges.
- Live sniffing / packet capture is decoupled: PCAP ingestion operates via authenticated HTTP upload (`POST /api/v1/telemetry/pcap`), while any physical network interface taps are isolated to dedicated DaemonSets with minimal scoped permissions.

---

## 4. Health Probe & Fail-Closed Matrix
- **Liveness Probe**: `GET /health` (Port 8000) — checks process health.
- **Readiness Probe**: `GET /api/v1/health/ready` (Port 8000) — checks Database and Redis connectivity.
- **Startup Probe**: `GET /health` with 30s initial window to allow ML artifact loading (`CatBoost`, `LightGBM`, `Random Forest`).
- **Fail-Closed Rule**: When `APP_ENV=production`, readiness probe returns 503 if Redis or Database is unreachable, preventing traffic routing to broken pods.

---

## 5. Graceful Shutdown & Redis Consumer Recovery
- Set `terminationGracePeriodSeconds: 60`.
- On `SIGTERM`, worker stops calling `XREADGROUP`, finishes in-flight ML predictions, and terminates.
- Any unacknowledged messages left in pending state are automatically reclaimed by survivor workers via `XAUTOCLAIM` / `claim_pending_events`.

---
*Created as required prior to manifest generation.*
