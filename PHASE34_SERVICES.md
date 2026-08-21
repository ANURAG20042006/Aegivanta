# PHASE 34 — RBVM SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `RBVMScoringService` | `backend/app/services/rbvm_scoring_service.py` | Multi-factor RBVM score calculator, SLA prioritization, asset exposure mappings. |
| `EPSSFeedService` | `backend/app/services/epss_feed_service.py` | EPSS 2.0 probability curves and CISA KEV catalog sync. |
| `VirtualPatchingService` | `backend/app/services/virtual_patching_service.py` | WAF/IPS virtual patching rule generator and enforcer. |
| `RBVMPostureService` | `backend/app/services/rbvm_posture_service.py` | Consolidated RBVM Posture Scorecard (0–100) and remediation campaign manager. |
