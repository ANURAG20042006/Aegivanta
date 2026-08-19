# SENTINELAI — PHASE 3.2 DISTRIBUTED STREAMING ARCHITECTURE
============================================================

## 1. Architecture Overview

SentinelAI Phase 3.2 introduces a production-ready, distributed streaming infrastructure backed by Redis Streams, Consumer Groups, Cross-Worker Atomic Idempotency, and a Multi-Instance Redis Pub/Sub WebSocket Backplane.

```mermaid
graph TD
    Sensor[PCAP Ingestion / Sensor Agents] -->|Event Payload| StreamEngine[DistributedStreamEngine]
    StreamEngine -->|SET NX EX| AtomicIdemp[Atomic Idempotency Gate (sentinel:idempotency:*)]
    AtomicIdemp -->|Unique Event| Stream[Redis Stream: sentinel:telemetry]
    AtomicIdemp -->|Duplicate| Drop[Reject Duplicate - 0 Recompute]
    
    Stream -->|XREADGROUP| WorkerA[Worker A: ML Inference & Feature Preprocessor]
    Stream -->|XREADGROUP| WorkerB[Worker B: ML Inference & Feature Preprocessor]
    
    WorkerA -->|Success| XACK_A[XACK sentinel:telemetry:group]
    WorkerB -->|Success| XACK_B[XACK sentinel:telemetry:group]
    
    WorkerA -->|Exhausted Retries| DLQ[Durable DLQ: sentinel:telemetry:dlq]
    WorkerB -->|Exhausted Retries| DLQ
    
    WorkerA -->|Threat Detected| PubSub[Redis Pub/Sub: sentinel:events]
    PubSub --> NodeA[API Node A -> Local WebSockets]
    PubSub --> NodeB[API Node B -> Local WebSockets]
```

## 2. Distributed Component Topology

| Component | Redis Key / Channel | Semantics | Failure Handling |
| :--- | :--- | :--- | :--- |
| **Telemetry Stream** | `sentinel:telemetry` | Append-only distributed event stream | Replicated, crash-resilient |
| **Consumer Group** | `sentinel:telemetry:group` | Competing consumer load partitioning | `XAUTOCLAIM` reclaims stale unacked messages |
| **Idempotency Gate**| `sentinel:idempotency:<sha256>`| Atomic Check-and-Set (`SET NX EX`) | 24-hour TTL automatic eviction |
| **Durable DLQ** | `sentinel:telemetry:dlq` | Persistent error ledger with attempts metadata | Replay endpoint re-queues event into stream |
| **WebSocket Backplane**| `sentinel:events` | Redis Pub/Sub broadcast | Non-blocking, decoupled node delivery |

## 3. Atomic Idempotency Guarantee
The SHA256 digest is deterministically computed from the 5-tuple, flow duration, forward packet count, and mean packet length.
Using Redis atomic `SET key "1" EX 86400 NX`, simultaneous delivery of duplicate flow vectors across disparate container workers is safely filtered with zero race conditions.
