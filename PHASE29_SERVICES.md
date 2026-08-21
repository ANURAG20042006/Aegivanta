# PHASE 29 — SUPPLY CHAIN SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `SBOMEngineService` | `backend/app/services/sbom_engine_service.py` | Generates CycloneDX 1.5 & SPDX 2.3 manifests, tracks component inventories. |
| `VEXEngineService` | `backend/app/services/vex_engine_service.py` | OpenVEX statement publisher and exploitability justifications. |
| `SLSAProvenanceService` | `backend/app/services/slsa_provenance_service.py` | SLSA Level 3 builder isolation and Cosign signature verification. |
| `CICDGatekeeperService` | `backend/app/services/cicd_gatekeeper_service.py` | Pipeline gatekeeper evaluation and high-entropy secret scanning. |
