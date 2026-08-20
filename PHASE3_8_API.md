# SENTINELAI — PHASE 3.8 REST API REFERENCE

## Threat Hunting & Investigation REST Endpoints

### 1. Threat Hunting Endpoints (`/api/v1/hunting`)

- `POST /api/v1/hunting/query`: Executes structured threat hunting query DSL.
- `GET /api/v1/hunting/hunts`: Lists all 10 modular hunt rules.
- `GET /api/v1/hunting/hunts/{hunt_id}`: Retrieves metadata for a specific hunt rule.
- `POST /api/v1/hunting/run/{hunt_id}`: Runs specific hunt rule against telemetry.
- `GET /api/v1/hunting/saved`: Lists saved search query templates.
- `POST /api/v1/hunting/saved`: Saves reusable query template.

### 2. Investigation Case Endpoints (`/api/v1/investigations`)

- `POST /api/v1/investigations`: Creates a new SOC investigation case.
- `GET /api/v1/investigations`: Lists cases with pagination and status/priority filters.
- `GET /api/v1/investigations/statistics`: Returns case operations statistics.
- `GET /api/v1/investigations/{id}`: Retrieves full case details with notes and evidence.
- `PATCH /api/v1/investigations/{id}`: Updates status, priority, or assigned analyst.
- `POST /api/v1/investigations/{id}/evidence`: Attaches evidence item to case.
- `GET /api/v1/investigations/{id}/evidence`: Lists attached evidence items.
- `POST /api/v1/investigations/{id}/pivot`: Executes multi-entity pivot search.
- `GET /api/v1/investigations/{id}/timeline`: Returns chronological event timeline.
- `GET /api/v1/investigations/{id}/graph`: Returns correlated evidence graph.
- `GET /api/v1/investigations/{id}/risk`: Returns explainable risk breakdown.
- `GET /api/v1/investigations/{id}/mitre`: Returns MITRE technique coverage.
- `POST /api/v1/investigations/{id}/notes`: Adds analyst note.
- `POST /api/v1/investigations/{id}/close`: Formally closes investigation case.
