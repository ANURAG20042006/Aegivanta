# Aegivanta — Phase 16: Threat Investigation Search Engine

## 1. Multi-Entity Unified Search
The investigation search engine coordinates high-performance bounded queries across 6 core entities:
1. `alerts`
2. `incidents`
3. `assets`
4. `threat_intel`
5. `rules`
6. `audit_logs`

## 2. Query Safety & Performance Limits
- **Bounded Result Sets**: Hard upper limit of 100 results per page (`limit <= 100`).
- **Query Latency Tracking**: Real-time measurement of query execution time (`query_latency_ms`).
- **Indexed Filters**: Fast filtering by severity, source IP, destination IP, asset ID, and text substring.

## 3. Endpoints
- `POST /api/v1/investigations/search`
- `GET /api/v1/investigations/search`
