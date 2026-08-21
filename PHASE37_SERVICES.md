# PHASE 37 — AI SOC AUTONOMY & UEBA SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `UEBAScoringService` | `backend/app/services/ueba_scoring_service.py` | Calculates dynamic User Risk Score (URS) from baseline deviations and anomalies. |
| `AISOCAutonomousInvestigator` | `backend/app/services/ai_soc_autonomous_investigator.py` | Autonomous incident triaging, hypothesis synthesis, and action approval orchestration. |
| `InsiderThreatDetectorService` | `backend/app/services/insider_threat_detector_service.py` | Detects mass downloads, unapproved cloud exfiltration, and privilege probing. |
| `AISOCPostureService` | `backend/app/services/ai_soc_posture_service.py` | Consolidated AI SOC Autonomy & UEBA Posture Scorecard (0–100). |
