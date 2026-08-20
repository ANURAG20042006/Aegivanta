# SENTINELAI — PHASE 3.3 PRODUCTION CONTAINER & NETWORK SECURITY
================================================================

## 1. Container Hardening Standards (`VERIFIED STATICALLY & LOCALLY`)

All SentinelAI Kubernetes manifests enforce the Pod Security Standards (PSS) `restricted` profile:

1. **Non-Root Execution**:
   - `runAsNonRoot: true`
   - `runAsUser: 10001` (API/Worker) and `999` (Redis)
   - `runAsGroup: 10001`
   - `fsGroup: 10001`
2. **Privilege Isolation**:
   - `allowPrivilegeEscalation: false`
   - `capabilities: { drop: ["ALL"] }`
   - Zero `CAP_NET_RAW` or root capabilities granted to API or ML worker pods.
3. **Seccomp Profile**:
   - `seccompProfile: { type: "RuntimeDefault" }`
4. **Filesystem Immutability**:
   - `readOnlyRootFilesystem: true`
   - Writable directories strictly scoped to ephemeral `emptyDir` volumes (`/tmp`, `/app/logs`, `/app/reports`).

---

## 2. Secrets & Zero-Credential Policy (`VERIFIED STATICALLY & LOCALLY`)

- **No Committed Secrets**: `secret-template.yaml` contains only placeholder values (`CHANGE_ME_*`).
- **Separation of Concerns**: Non-sensitive application configuration resides in `k8s/configmap.yaml`, while database credentials and signing keys are isolated in Kubernetes Secrets.
- **Fail-Closed Readiness**: When `APP_ENV=production`, the application immediately reports `503 Service Unavailable` if Redis or the database is inaccessible, preventing unauthenticated or corrupted flow processing.

---

## 3. Kubernetes Network Micro-Segmentation (`VERIFIED STATICALLY`)

The `sentinelai-network-policy` isolates network communications:
- Ingress to `sentinelai-api` permitted only from the Ingress Controller on TCP port `8000`.
- Ingress to `sentinelai-redis` permitted only from `sentinelai-api` and `sentinelai-worker` pods on TCP port `6379`.
- Direct exposure of PostgreSQL or Redis to external internet traffic is strictly prohibited.
- Egress allows DNS resolution (port 53), Redis traffic (port 6379), and database traffic (port 5432).
