# PHASE 32 — CTI 2.0 SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `STIXTAXIIEngineService` | `backend/app/services/stix_taxii_engine_service.py` | STIX 2.1 JSON parser, TAXII 2.1 poll orchestrator, indicator deduplication. |
| `ThreatActorProfilingService` | `backend/app/services/threat_actor_profiling_service.py` | Threat actor intelligence library, Diamond Model generator, campaign attribution. |
| `IOCDecayService` | `backend/app/services/ioc_decay_service.py` | Exponential time decay, sighting correlation, confidence recalculation. |
| `CTIPostureService` | `backend/app/services/cti_posture_service.py` | Consolidated CTI 2.0 Posture Scorecard and automated hunting query generation. |
