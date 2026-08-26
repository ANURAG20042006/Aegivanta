# Aegivanta — Phase 11: Global Distributed Scaling Architecture

## 1. Stream Partitioning & Consumer Groups
Aegivanta decouples ingestion from detection via Redis Streams:
- **Telemetry Stream**: `sentinelai:telemetry`
- **Detection Stream**: `sentinelai:detection`
- **Threat Intel Stream**: `sentinelai:threat_intel`
- **Response Stream**: `sentinelai:response`
- **Hunting Stream**: `sentinelai:hunting`
- **Audit Stream**: `sentinelai:audit`

## 2. Horizontal Pod Autoscaling (HPA)
Each worker role runs in dedicated Kubernetes Deployments scaled by CPU and Redis stream consumer lag:
- `sentinelai-api-hpa`: Min 2, Max 10
- `sentinelai-detection-worker-hpa`: Min 2, Max 15
- `sentinelai-response-worker-hpa`: Min 2, Max 6

## 3. Fault Tolerance & Dead-Letter Queues (DLQ)
- **Orphan Message Recovery**: `XAUTOCLAIM` periodically claims unacknowledged messages after 60s idle timeout.
- **Dead-Letter Queue Routing**: Repeatedly failing events (exceeding `max_retries`) are routed to `sentinelai:dl_queue:<role>` with error metadata and capped at 10,000 entries.
