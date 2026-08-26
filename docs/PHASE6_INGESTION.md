# Aegivanta Phase 6 — High-Throughput Telemetry Ingestion Pipeline

## 1. Supported Event Types

| Telemetry Type | Description | Mandatory Schema Fields |
|---|---|---|
| `NETWORK_FLOW` | IP 5-tuple bidirectional network sessions | `src_ip`, `dst_ip`, `src_port`, `dst_port`, `protocol` |
| `AUTH_EVENT` | User logins, privilege elevations, SSH/RDP attempts | `user`, `src_ip`, `success` |
| `DNS_QUERY` | Forward & reverse DNS resolution records | `query_name`, `query_type` |
| `HTTP_METADATA` | Web transactions, URLs, response codes | `method`, `host`, `uri`, `status_code` |
| `PROCESS_EVENT` | Process executions, parent-child hierarchies | `pid`, `executable_path` |
| `SYSTEM_EVENT` | Service creations, kernel modules, firewall changes | `event_type`, `description` |

## 2. Ingestion Endpoint
- `POST /api/v1/sensors/ingest`
- **Headers**:
  - `X-Sensor-ID`: Unique sensor UUID
  - `X-Sensor-Token`: Cryptographic enrollment token
  - `Content-Encoding`: `gzip` or `deflate` (optional)
