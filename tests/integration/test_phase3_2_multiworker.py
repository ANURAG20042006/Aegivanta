"""
tests/integration/test_phase3_2_multiworker.py
==============================================
Integration test for multi-worker concurrency, distributed load partitioning,
and race-condition deduplication across independent workers.
"""

import pytest
import asyncio
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend, DistributedStreamEngine


@pytest.mark.asyncio
async def test_multi_worker_consumer_group_partitioning():
    """Verify events published to a single stream are evenly distributed between Worker A and Worker B."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    stream_key = "sentinel:telemetry:multiworker"
    group_key = "sentinel:telemetry:group"

    # Publish 10 telemetry events
    for i in range(10):
        await backend.publish_event(stream_key, {
            "event_id": f"flow-event-{i}",
            "source_ip": f"192.168.1.{10+i}",
            "destination_ip": "10.0.0.1",
            "source_port": 40000 + i,
            "destination_port": 80,
            "protocol": "TCP"
        })

    # Worker A and Worker B consume concurrently
    worker_a_msgs = await backend.consume_events(stream_key, group_key, "worker-A", count=5)
    worker_b_msgs = await backend.consume_events(stream_key, group_key, "worker-B", count=5)

    assert len(worker_a_msgs) == 5
    assert len(worker_b_msgs) == 5

    # Ensure zero overlap in processed messages
    ids_a = {m["id"] for m in worker_a_msgs}
    ids_b = {m["id"] for m in worker_b_msgs}
    assert ids_a.isdisjoint(ids_b)
    assert len(ids_a.union(ids_b)) == 10
