# SentinelAI — Final Production REST & WebSocket API Documentation

## Base URL: `/api/v1`

---

## 1. Authentication & Users (`/auth`, `/users`)
- `POST /auth/login`: Authenticates user and issues JWT Bearer token.
- `POST /auth/logout`: Revokes token and logs session termination.
- `GET /auth/me`: Returns authenticated user profile and roles.
- `GET /users`: Lists platform users (Admin only).

## 2. Telemetry & Predictions (`/telemetry`, `/predict`)
- `POST /telemetry/stream`: Ingests real-time network flow telemetry.
- `POST /predict/single`: Performs real-time multi-model classification on a 30-feature flow vector.
- `POST /predict/batch`: High-throughput batch inference.

## 3. Incident Management & Correlation (`/incidents`, `/alerts`)
- `GET /incidents`: Lists incidents with status, severity, and time-range filtering.
- `GET /incidents/{id}`: Retrieves comprehensive incident dossier.
- `PATCH /incidents/{id}`: Updates incident status or assigned analyst.
- `GET /alerts`: Lists correlated security alert detections.

## 4. Threat Intelligence (`/threat-intel`)
- `GET /threat-intel/indicators`: Searches active threat indicators.
- `POST /threat-intel/indicators`: Manually adds IOC indicator.
- `GET /threat-intel/feeds`: Feed health and sync status.
- `POST /threat-intel/sync`: Triggers manual threat feed synchronization.

## 5. Attack Graph & Lateral Movement (`/threat-graph`)
- `GET /threat-graph`: Traverses entity relationship graph.
- `GET /threat-graph/lateral-movement/{source_ip}`: Identifies multi-hop lateral attack paths.
- `GET /threat-graph/blast-radius/{entity_id}`: Computes downstream impact radius.

## 6. SOAR & Remediation Engine (`/response`, `/playbooks`)
- `GET /response/actions`: Lists pending and executed response actions.
- `POST /response/actions`: Initiates remediation action.
- `POST /response/actions/{id}/approve`: Approves high-impact action (Admin only).
- `POST /response/actions/{id}/rollback`: Executes action rollback (Admin only).

## 7. Threat Hunting & Investigations (`/hunting`, `/investigations`)
- `POST /hunting/query`: Executes safe whitelist query DSL.
- `GET /hunting/hunts`: Lists 10 production hunting rules.
- `POST /hunting/run/{hunt_id}`: Runs hunting rule.
- `POST /investigations`: Creates investigation case.
- `GET /investigations/{id}`: Returns case details, notes, evidence, timeline, and graph.
- `POST /investigations/{id}/evidence`: Attaches evidence item.
- `POST /investigations/{id}/notes`: Adds analyst note.
- `POST /investigations/{id}/close`: Closes investigation case.

## 8. Adaptive ML & Governance (`/adaptive-ml`)
- `POST /adaptive-ml/detect`: Performs ensemble multi-signal detection.
- `GET /adaptive-ml/models`: Lists model registry status.
- `POST /adaptive-ml/feedback`: Submits human-in-the-loop analyst feedback.
- `POST /adaptive-ml/models/{id}/promote`: Promotes model to production.
- `POST /adaptive-ml/models/{id}/rollback`: Rolls back champion model.

## 9. Dashboard Aggregation (`/dashboard`)
- `GET /dashboard/overview`: 8 real-time SOC metrics and KPIs.
- `GET /dashboard/incidents`: Incident command center aggregation.
- `GET /dashboard/mitre`: MITRE ATT&CK coverage matrix heatmap.
- `GET /dashboard/threat-intel`: Fast IOC cache and feed status.
- `GET /dashboard/response`: SOAR approvals queue and latency statistics.
- `GET /dashboard/system-health`: Sanitized subsystem latency and status.

## 10. WebSockets
- `WS /ws/soc-events`: Real-time bidirectional SOC event stream (heartbeat, snapshot, 12 event types).
