# AEGIVANTA — SYSTEM ARCHITECTURE SPECIFICATION

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  

---

## 1. End-to-End System Topology

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|  React 18 + Vite Commercial SPA (Dark SOC UI, WebSockets, Lucide, Tailwind CSS)   |
+------------------------------------------+----------------------------------------+
                                           | HTTPS / WSS
                                           v
+-----------------------------------------------------------------------------------+
|                              API GATEWAY TIER                                     |
|  FastAPI Gateway (Uvicorn, Asynchronous ASGI, OpenAPI Docs, Prometheus Metrics)  |
|  - Rate Limiting (In-Memory + Redis)                                              |
|  - JWT Bearer Authentication & RBAC Authorization Gate                            |
|  - Structured Logging Context (Correlation ID, Trace ID, User Context)            |
+------------------------------------------+----------------------------------------+
                                           |
                 +-------------------------+-------------------------+
                 |                                                   |
                 v                                                   v
+----------------------------------+               +----------------------------------+
|      PERSISTENCE STORAGE         |               |   DISTRIBUTED STREAMING BROKER   |
|  PostgreSQL 16 / SQLite Async    |               |   Redis 7 Streams & Pub/Sub      |
|  - Users & Audit Logs            |               |   - Stream: aegivanta:telemetry  |
|  - Incidents & Evidence Timeline |               |   - Consumer Group: workers      |
|  - Asset Inventory & Status      |               |   - Dead Letter Queue (DLQ)      |
|  - Playbook Run History          |               |   - Event Pub/Sub Channel        |
+----------------------------------+               +-----------------+----------------+
                                                                     |
                                           +-------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                         DISTRIBUTED WORKER SERVICES                               |
|  - ML Inference Worker: CatBoost Model (30 features, TreeSHAP Explainability)    |
|  - Threat Intel Worker: IOC Fast Cache (IP, Domain, SHA256) & Feed Sync           |
|  - Detection Correlation Engine: Temporal 300s windowing & Risk Scoring (0–100)   |
|  - Attack Graph Service: Lateral movement reachability & blast-radius traversal  |
|  - Autonomous SOAR Worker: Playbook execution, dry-run simulation & rollback      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Design & Responsibilities

### 1. Ingestion Pipeline
- Accepts 5-tuple IP flow records and binary PCAP uploads (`/api/v1/telemetry/ingest`, `/api/v1/telemetry/pcap/upload`).
- Generates SHA-256 idempotency fingerprint from source IP, target IP, ports, protocol, duration, and packet counts.
- Atomically checks idempotency in Redis (`check_and_set_idempotency`) with a 24-hour TTL.

### 2. Threat Detection & XAI Pipeline
- Validates incoming feature vectors against `ml.schema.feature_schema.FLOW_FEATURE_COLUMNS` (30 features).
- CatBoost champion model evaluates attack probability and class prediction.
- TreeSHAP computes local Shapley values to identify top 5 feature contributions without synthetic estimation.

### 3. Threat Intelligence & Incident Correlation
- Checks IP addresses and hashes against `ThreatIntelService` in-memory lookup table and active IOC feeds.
- If malicious activity is flagged, `DetectionCorrelationEngine` groups related signals within a 300s sliding window into an `Incident` entity.
- Computes deterministic incident risk score (0–100) via `RiskScoringService`.

### 4. Attack Graph & Blast Radius
- Builds in-memory directed graphs linking assets, IP flows, and observed MITRE ATT&CK techniques.
- Calculates multi-hop lateral movement pathways using shortest-path graph algorithms.

### 5. Autonomous SOAR & Safety
- Evaluates configured response policies against incident risk, target asset criticality, and attack category.
- Executes containment actions (`BLOCK_IP`, `ISOLATE_HOST`, etc.) in simulated dry-run or authorized live execution mode.
- Records rollback state snapshots in `PlaybookExecution` database table for instant reversal.
