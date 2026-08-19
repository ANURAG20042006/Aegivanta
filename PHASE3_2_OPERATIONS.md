# SENTINELAI — PHASE 3.2 STREAMING OPERATIONS MANUAL
===================================================

## 1. Operational Configuration

Set the following environment variables in production:
```bash
REDIS_URL=redis://:strong_password@redis-cluster.prod:6379/0
REDIS_SSL=true
STREAM_TELEMETRY_KEY=sentinel:telemetry
STREAM_CONSUMER_GROUP=sentinel:telemetry:group
STREAM_DLQ_KEY=sentinel:telemetry:dlq
STREAM_PUBSUB_CHANNEL=sentinel:events
STREAM_MAX_RETRIES=3
STREAM_IDEMPOTENCY_TTL_SECONDS=86400
```

## 2. Inspecting and Replaying Dead Letter Queue (DLQ)

### List DLQ Entries
```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/health/metrics
```

### Replay a Dead Letter Event
```python
from backend.app.services.distributed_stream_service import distributed_stream_engine
import asyncio

async def replay(dlq_id):
    res = await distributed_stream_engine.replay_dlq_event(dlq_id)
    print("Replay result:", res)

asyncio.run(replay("dlq-message-id"))
```

## 3. Monitoring Metrics
Prometheus scrapes `/api/v1/metrics/prometheus`:
- `sentinel_redis_connected`: 1 (Healthy) or 0 (Degraded/Offline)
- `sentinel_stream_published_total`
- `sentinel_stream_consumed_total`
- `sentinel_stream_acked_total`
- `sentinel_stream_retried_total`
- `sentinel_stream_duplicates_total`
- `sentinel_stream_dlq_total`
- `sentinel_websocket_broadcast_total`
