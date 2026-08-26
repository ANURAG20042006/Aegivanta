# PHASE 32 — CTI 2.0 API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/threat-intel-v2/summary` | Consolidated CTI 2.0 Posture & Threat Landscape Scorecard. |
| `GET` | `/api/v1/threat-intel-v2/actors` | List nation-state and eCrime threat actor profiles with Diamond Model. |
| `GET` | `/api/v1/threat-intel-v2/feeds` | List registered STIX 2.1 / TAXII 2.1 threat feed subscriptions. |
| `POST` | `/api/v1/threat-intel-v2/feeds/poll/{id}` | Manually trigger on-demand TAXII feed poll and ingestion. |
| `GET` | `/api/v1/threat-intel-v2/indicators` | List CTI indicators with real-time decayed confidence scores. |
| `GET` | `/api/v1/threat-intel-v2/campaigns/heatmap` | List MITRE ATT&CK campaign technique heat levels. |
| `POST` | `/api/v1/threat-intel-v2/hunting/generate-queries` | Synthesize KQL and SPL threat hunting queries for target actor. |
