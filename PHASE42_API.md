# PHASE 42 — MULTI-REGION RESILIENCE API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/multi-region/summary` | Consolidated Multi-Region Resilience Posture Scorecard. |
| `GET` | `/api/v1/multi-region/clusters` | List multi-region replication clusters. |
| `POST` | `/api/v1/multi-region/failover` | Trigger instantaneous active-active regional failover. |
| `GET` | `/api/v1/multi-region/failover-events` | List historical regional failover execution events. |
| `GET` | `/api/v1/multi-region/residency` | List sovereign data residency boundaries. |
| `POST` | `/api/v1/multi-region/residency` | Create a new sovereign data residency boundary. |
