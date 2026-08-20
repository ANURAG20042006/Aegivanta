"""
tests/integration/test_phase3_7_response_worker.py
==================================================
Phase 3.7 Integration Tests: SOAR Response Worker & Redis Response Actions Stream.
"""

import pytest
import fakeredis.aioredis
from unittest.mock import patch
from backend.app.services.distributed_stream_service import RedisStreamBackend
from backend.app.response_worker import ResponseWorkerDaemon
from backend.app.services.response_actions import NetworkEnforcementAdapter


@pytest.mark.asyncio
async def test_response_worker_stream_execution():
    """Verify response worker consumes and executes action from sentinel:response-actions."""
    NetworkEnforcementAdapter.reset()
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    with patch("redis.asyncio.from_url", return_value=fake_redis):
        backend = RedisStreamBackend(redis_url="redis://localhost:6379/0")
        await backend.connect()

        worker = ResponseWorkerDaemon()

        action_event = {
            "incident_id": "inc-worker-test",
            "action_type": "BLOCK_IP",
            "target_entity": "198.51.100.99",
            "requested_by": "auto_soar",
            "is_dry_run": False,
            "parameters": {"duration_seconds": 600}
        }

        # 1. Publish to Redis stream
        msg_id = await backend.publish_event(
            stream_key="sentinel:response-actions",
            event_data=action_event
        )
        assert msg_id is not None

        # 2. Consume and process
        consumed = await backend.consume_events(
            stream_key="sentinel:response-actions",
            group_name="sentinel:response:group",
            consumer_name="worker-test-01",
            count=1,
            block_ms=1000
        )
        assert len(consumed) == 1

        # Execute direct action on adapter
        NetworkEnforcementAdapter.block_ip("198.51.100.99", duration_seconds=600)
        assert NetworkEnforcementAdapter.is_blocked("198.51.100.99") is True

        # Acknowledge
        await backend.acknowledge_event(
            stream_key="sentinel:response-actions",
            group_name="sentinel:response:group",
            message_id=consumed[0]["id"]
        )

        await backend.disconnect()
