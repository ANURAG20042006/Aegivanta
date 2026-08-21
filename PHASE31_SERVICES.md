# PHASE 31 — ATTACK SURFACE & CTEM SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `ExternalReconService` | `backend/app/services/external_recon_service.py` | External asset discovery, open port scanning, SSL health, and dangling DNS checks. |
| `CTEMPrioritizationService` | `backend/app/services/ctem_prioritization_service.py` | Gartner 5-Stage CTEM engine combining EPSS, CVSS v3.1, and CISA KEV weaponization. |
| `DarkWebBrandMonitorService` | `backend/app/services/darkweb_brand_monitor_service.py` | Dark web credential breach detection, pastebin monitoring, and typosquatted lookalikes. |
| `ASMPostureService` | `backend/app/services/asm_posture_service.py` | Consolidated External Exposure Index (0–100) and top mobilization actions. |
