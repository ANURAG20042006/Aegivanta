# PHASE 41 — GLOBAL EDGE INGESTION FABRIC SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `EdgeFabricService` | `backend/app/services/edge_fabric_service.py` | PoP node registry, throughput aggregation, geo-routing management, and regional WAN route mapping. |
| `EdgeInspectionService` | `backend/app/services/edge_inspection_service.py` | Edge-side WAF & DDoS scrubbing policy evaluation, rate limiting, and geo-fencing controls. |
| `EdgeSecurityPostureService` | `backend/app/services/edge_security_posture_service.py` | Evaluates consolidated edge security posture scorecard (0–100). |
