# PHASE 36 — MICROSEGMENTATION & ZTNA SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `ZTNAControllerService` | `backend/app/services/ztna_controller_service.py` | SDP connector gateway fleet manager, identity-bound client sessions, revocation. |
| `MicrosegmentationPolicyService` | `backend/app/services/microsegmentation_policy_service.py` | L4/L7 policy compiler, eBPF kernel rule table generator. |
| `LateralMovementDetectorService` | `backend/app/services/lateral_movement_detector_service.py` | Lateral movement defense analyzer, network flow topology mesh graph provider. |
| `MicrosegmentationPostureService` | `backend/app/services/microsegmentation_posture_service.py` | Consolidated ZTNA & Microsegmentation Posture Scorecard (0–100). |
