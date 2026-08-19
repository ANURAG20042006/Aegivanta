"""
tests/integration/test_phase3_2_failure_recovery.py
===================================================
Integration test for worker failure recovery and abandoned pending message reclamation.
"""

import pytest
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend, InMemoryStreamBackend


@pytest.mark.asyncio
async def test_pending_message_reclamation_after_worker_crash():
    """Verify abandoned message from crashed worker is reclaimed by healthy worker via claim_pending_events."""
    backend = InMemoryStreamBackend()
    stream_key = "sentinel:telemetry:crash"
    group_name = "sentinel:telemetry:group"

    # 1. Publish event
    await backend.publish_event(stream_key, {"event_id": "crash-event-1", "src": "1.1.1.1"})

    # 2. Worker 1 consumes message but crashes before XACK
    w1_msgs = await backend.consume_events(stream_key, group_name, "crashed-worker-1", count=1)
    assert len(w1_msgs) == 1

    # 3. Healthy Worker 2 claims pending abandoned messages (idle threshold 0ms for test)
    reclaimed = await backend.claim_pending_events(
        stream_key=stream_key,
        group_name=group_name,
        consumer_name="healthy-worker-2",
        min_idle_time_ms=0,
        count=5
    )
    assert len(reclaimed) == 1
    assert reclaimed[0]["claimed_by"] == "healthy-worker-2"
    assert reclaimed[0]["data"]["event_id"] == "crash-event-1"

    # 4. Healthy Worker 2 successfully acknowledges the event
    ack_res = await backend.acknowledge_event(stream_key, group_name, reclaimed[0]["id"])
    assert ack_res is True
