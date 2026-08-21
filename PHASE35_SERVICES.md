# PHASE 35 — DLP SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `DLPInspectionService` | `backend/app/services/dlp_inspection_service.py` | Luhn credit card validator, SSN context parser, cloud secret scanner, payload sanitizer. |
| `TokenizationVaultService` | `backend/app/services/tokenization_vault_service.py` | Format-preserving token generator, AES-256-GCM vault, RBAC detokenizer. |
| `DSPMShadowDataService` | `backend/app/services/dspm_shadow_data_service.py` | Cloud storage & database shadow data discovery, unencrypted exposure analyzer. |
| `DLPPostureService` | `backend/app/services/dlp_posture_service.py` | Consolidated DLP Posture Scorecard (0–100) and data protection metric aggregator. |
