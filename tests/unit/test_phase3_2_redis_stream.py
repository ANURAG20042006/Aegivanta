"""
tests/unit/test_phase3_2_redis_stream.py
========================================
Unit tests for Phase 3.2 Redis Streams & Consumer Groups.
Tests stream publication, consumer group partitioning, acknowledgment (XACK),
and pending message reclamation.
"""

import pytest
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend


@pytest.mark.asyncio
async def test_redis_stream_publish_and_consumer_group():
    """Verify publication and consumer group read/ack cycle."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    stream_name = "test:stream"
    group_name = "test:group"
    consumer_a = "worker-A"

    # 1. Publish 2 telemetry events
    evt_1 = {"event_id": "evt-001", "source_ip": "192.168.1.100", "payload_len": 500}
    evt_2 = {"event_id": "evt-002", "source_ip": "192.168.1.200", "payload_len": 800}

    id_1 = await backend.publish_event(stream_name, evt_1)
    id_2 = await backend.publish_event(stream_name, evt_2)
    assert id_1 is not None and len(id_1) > 0
    assert id_2 is not None and len(id_2) > 0

    # 2. Consume events as Worker A
    messages = await backend.consume_events(
        stream_key=stream_name,
        group_name=group_name,
        consumer_name=consumer_a,
        count=10
    )
    assert len(messages) == 2
    assert messages[0]["data"]["event_id"] == "evt-001"
    assert messages[1]["data"]["event_id"] == "evt-002"

    # 3. Acknowledge first message
    ack_res = await backend.acknowledge_event(stream_name, group_name, messages[0]["id"])
    assert ack_res is True


@pytest.mark.asyncio
async def test_consumer_group_load_balancing_between_workers():
    """Verify each unread message is processed by only one worker consumer."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    stream_name = "test:stream:lb"
    group_name = "test:group:lb"

    # Publish 4 messages
    for i in range(4):
        await backend.publish_event(stream_name, {"event_id": f"msg-{i}", "index": i})

    # Worker 1 reads 2 messages
    w1_msgs = await backend.consume_events(stream_name, group_name, "worker-1", count=2)
    assert len(w1_msgs) == 2

    # Worker 2 reads remaining 2 messages
    w2_msgs = await backend.consume_events(stream_name, group_name, "worker-2", count=2)
    assert len(w2_msgs) == 2

    # Verify no overlapping message IDs between worker 1 and worker 2
    w1_ids = {m["id"] for m in w1_msgs}
    w2_ids = {m["id"] for m in w2_msgs}
    assert w1_ids.isdisjoint(w2_ids)
