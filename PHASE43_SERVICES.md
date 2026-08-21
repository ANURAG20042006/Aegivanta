# PHASE 43 — DATA GOVERNANCE & DSAR SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `DataLineageService` | `backend/app/services/data_lineage_service.py` | Lineage recording, transformation hash provenance, and stage audit. |
| `LegalHoldService` | `backend/app/services/legal_hold_service.py` | Forensic evidence legal hold custody and artifact freezing. |
| `DSARWorkflowService` | `backend/app/services/dsar_workflow_service.py` | GDPR/CCPA personal data discovery, access exports, and right-to-be-forgotten purges. |
| `DataGovernancePostureService` | `backend/app/services/data_governance_posture_service.py` | Consolidated Governance & DSAR Posture Scorecard (0–100). |
