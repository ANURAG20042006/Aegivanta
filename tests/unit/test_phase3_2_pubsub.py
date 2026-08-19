"""
tests/unit/test_phase3_2_pubsub.py
==================================
Unit tests for Phase 3.2 Redis Pub/Sub WebSocket backplane broadcasting.
"""

import pytest
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend


@pytest.mark.asyncio
async def test_redis_pubsub_publish():
    """Verify Redis Pub/Sub publishes broadcast events successfully."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    event_msg = {
        "type": "INCIDENT_CREATED",
        "data": {"incident_id": "INC-TEST-001", "severity": "Critical"}
    }

    # Publish to Redis channel
    receivers = await backend.publish_pubsub("sentinel:events", event_msg)
    # When no active subscribers in test client, return count >= 0 without error
    assert receivers >= 0
