# AEGIVANTA — PHASE 18 REST API SPECIFICATION

## 1. Threat Intelligence Platform Endpoints
- `GET /api/v1/threat-intelligence/actors`: List profiled threat actors.
- `POST /api/v1/threat-intelligence/actors`: Create new adversary profile.
- `GET /api/v1/threat-intelligence/campaigns`: List attack campaigns.
- `POST /api/v1/threat-intelligence/campaigns`: Register coordinated campaign.
- `POST /api/v1/threat-intelligence/correlate`: Cross-correlate IOC with active alerts and sightings.
- `POST /api/v1/threat-intelligence/sightings`: Record empirical customer network sighting.
- `POST /api/v1/threat-intelligence/feeds/{id}/sync`: Trigger feed synchronization.

## 2. Threat Hunting Workbench Endpoints
- `GET /api/v1/hunting-workbench/templates`: List standard parameterized hunting query templates.
- `POST /api/v1/hunting-workbench/execute`: Execute multi-entity threat hunt with execution telemetry.
