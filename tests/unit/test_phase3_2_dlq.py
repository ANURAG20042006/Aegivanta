"""
tests/unit/test_phase3_2_dlq.py
===============================
Unit tests for Phase 3.2 Durable Dead Letter Queue (DLQ), retry exponential backoff,
inspection, deletion, and DLQ event replay.
"""

import pytest
import fakeredis.aioredis
from backend.app.config import settings
from backend.app.services.distributed_stream_service import RedisStreamBackend, DistributedStreamEngine


@pytest.mark.asyncio
async def test_durable_dlq_persistence_and_retry_exhaustion():
    """Verify failed events are retried with backoff and routed to DLQ after exhaustion."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    engine = DistributedStreamEngine(backend=backend)

    # Failing processor
    async def always_fails(data):
        raise ValueError("Simulated downstream failure")

    event_payload = {
        "event_id": "bad-flow-001",
        "source_ip": "1.2.3.4",
        "features": {"destination_ip": "10.0.0.1"}
    }

    success, res, err = await engine.process_with_retry(
        event_payload,
        processor_fn=always_fails,
        max_retries=3
    )

    assert success is False
    assert "Simulated downstream failure" in str(err)
    assert engine.metrics["retried_total"] == 3
    assert engine.metrics["dlq_total"] == 1

    # Verify message in DLQ
    dlq_entries = await backend.list_dlq(settings.STREAM_DLQ_KEY, count=10)
    assert len(dlq_entries) == 1
    assert dlq_entries[0]["event_id"] == "bad-flow-001"
    assert "Simulated downstream failure" in dlq_entries[0]["failure_reason"]


@pytest.mark.asyncio
async def test_dlq_event_replay():
    """Verify dead-lettered event can be replayed and re-queued into active stream."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    engine = DistributedStreamEngine(backend=backend)

    # 1. Insert failed event into DLQ
    dlq_id = await backend.push_to_dlq(
        dlq_key=settings.STREAM_DLQ_KEY,
        event_payload={"event_id": "replay-evt-101", "source_ip": "10.10.10.10", "total_fwd_packets": 5},
        reason="Initial parsing exception",
        attempts=3,
        source_worker="worker-1"
    )

    # 2. Replay DLQ event
    replay_res = await engine.replay_dlq_event(dlq_message_id=dlq_id)
    assert replay_res["status"] == "REPLAYED"

    # 3. Verify event is removed from DLQ
    remaining = await backend.list_dlq(settings.STREAM_DLQ_KEY, count=10)
    assert len(remaining) == 0
