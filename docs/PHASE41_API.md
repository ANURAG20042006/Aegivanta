# PHASE 41 — EDGE SECURITY FABRIC API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/edge-fabric/summary` | Consolidated Global Edge Security Posture Scorecard. |
| `GET` | `/api/v1/edge-fabric/pops` | List active global edge PoP ingestion nodes. |
| `GET` | `/api/v1/edge-fabric/policies` | List edge inspection & DDoS mitigation policies. |
| `POST` | `/api/v1/edge-fabric/policies` | Deploy a new edge inspection & DDoS mitigation policy. |
| `GET` | `/api/v1/edge-fabric/routes` | List regional ingestion routes to primary core clusters. |
