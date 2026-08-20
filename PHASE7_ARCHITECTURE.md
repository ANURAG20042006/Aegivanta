# Aegivanta — Phase 7: Security Data Plane & Sensor Fleet Architecture

## 1. Overview
The Security Data Plane is responsible for high-throughput, fault-tolerant telemetry ingestion from distributed customer sensor fleets (Linux, Windows, Kubernetes, and Cloud Gateways).

```
[ Customer Sensor Daemon ]
       | (TLS 1.3 + Gzip/Deflate + Rotating Token Header)
       v
[ POST /api/v1/sensors/ingest ]
       |
       +---> [ Gzip/Deflate Decompression Engine (Bounded <= 10MB) ]
       |
       +---> [ Multi-Schema Validator (FLOW, AUTH, DNS, HTTP, PROCESS) ]
       |
       +---> [ Sliding-Window LRU Deduplication Cache (50,000 hashes) ]
       |
       +---> [ Usage Metering Service (events_ingested accumulator) ]
       |
       +---> [ Sensor Health & Heartbeat Tracker ]
       |
       v
[ Redis Stream: sentinelai:telemetry ]
```

## 2. Ingestion Schemas
Supported telemetry schemas include:
1. `NETWORK_FLOW`: 5-tuple (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `protocol`), byte counts, packet counts.
2. `AUTH_EVENT`: User, source IP, authentication status, auth mechanism.
3. `DNS_QUERY`: Query domain, query type (A, AAAA, TXT, MX), response code.
4. `HTTP_METADATA`: Method, host, URI path, status code, user-agent.
5. `PROCESS_EVENT`: PID, PPID, executable path, command line arguments, parent executable.
6. `SYSTEM_EVENT`: CPU/memory metrics, OS audit events, daemon status.

## 3. Idempotency and Ordering
- Events are sorted by `seq_id` and ISO 8601 `timestamp` prior to streaming.
- Event hashes are generated using SHA-256 over `(sensor_id, event_type, sorted_data_json)` to prevent duplicate ingestion during network retries.
