# Aegivanta Phase 6 — Real-Time Security Data & Sensor Ecosystem Architecture

## 1. System Overview

Aegivanta Phase 6 provides a resilient, multi-tenant telemetry ingestion architecture capable of ingesting high-volume compressed security events from endpoints, network mirrors, cloud taps, and Kubernetes clusters.

```
+-----------------------------------------------------------------------------------+
|                        AEGIVANTA SENSOR FLEET & AGENTS                            |
|                                                                                   |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  | Endpoint EDR Agent |  | Network TAP (PCAP) |  | Kubernetes eBPF DaemonSet   |  |
|  +---------+----------+  +---------+----------+  +--------------+--------------+  |
+------------|-----------------------|----------------------------|-----------------+
             |                       |                            |
             | (Gzip Batched Events) | (Direct Streaming)         | (Compressed)
             +-----------------------+----------------------------+
                                     |
                                     v
+-----------------------------------------------------------------------------------+
|                      HIGH-PERFORMANCE INGESTION GATEWAY                           |
|                        (POST /api/v1/sensors/ingest)                              |
|                                                                                   |
|  +---------------------------+  +--------------------------+  +----------------+  |
|  | Decompression (Gzip/Zlib) |  | Sensor Token & Tenant    |  | Rate Limiter / |  |
|  | Max 10MB Expansion Limit  |  | Authentication           |  | Backpressure   |  |
|  +-------------+-------------+  +------------+-------------+  +--------+-------+  |
|                |                             |                         |          |
|                +-----------------------------+-------------------------+          |
|                                              |                                    |
|                                              v                                    |
|  +-----------------------------------------------------------------------------+  |
|  | Multi-Source Schema Validation (Flow, Auth, DNS, HTTP, Process, System)    |  |
|  +-------------------------------------------+---------------------------------+  |
|                                              |                                    |
|                                              v                                    |
|  +-----------------------------------------------------------------------------+  |
|  | SHA-256 LRU Event Deduplication & Monotonic Sequence Number Sorter         |  |
|  +-------------------------------------------+---------------------------------+  |
|                                              |                                    |
|                                              v                                    |
|  +-----------------------------------------------------------------------------+  |
|  | Tenant Usage Metering Buffer & Quota Check                                  |  |
|  +-------------------------------------------+---------------------------------+  |
+----------------------------------------------|------------------------------------+
                                               |
                                               v
+-----------------------------------------------------------------------------------+
|                        REDIS STREAM INGESTION BROKER                              |
|                       (telemetry:stream -> ML Workers)                            |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Capabilities

1. **Lightweight Standalone Customer Agent (`scripts/aegivanta_agent.py`)**: Zero-pip dependency Python 3 daemon with automatic local buffering, heartbeats, and gzip-compressed batching.
2. **Schema Engine**: Multi-event schema validation across 6 telemetry types: `NETWORK_FLOW`, `AUTH_EVENT`, `DNS_QUERY`, `HTTP_METADATA`, `PROCESS_EVENT`, `SYSTEM_EVENT`.
3. **Resilience & Deduplication**: Sliding-window LRU SHA-256 hash deduplication ensures zero event loss and zero duplicate detections during network retry bursts.
4. **Sensor Fleet Health Management**: Real-time fleet health scoring (0–100), online status monitoring, OTA version upgrade scheduling, and cross-platform installation scripts.
