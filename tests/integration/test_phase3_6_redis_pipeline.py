"""
tests/integration/test_phase3_6_redis_pipeline.py
=================================================
Phase 3.6 Integration Tests: Worker Correlation Pipeline & Redis Incidents Stream.
Verifies telemetry processing, rule evaluation, and publishing to sentinel:incidents.
"""

import pytest
import fakeredis.aioredis
from unittest.mock import patch
from backend.app.services.distributed_stream_service import RedisStreamBackend, DistributedStreamEngine
from backend.app.worker import StreamWorkerDaemon


@pytest.mark.asyncio
async def test_worker_telemetry_to_incident_stream_pipeline():
    """Verify worker processes telemetry and publishes correlated bundle to sentinel:incidents."""
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    with patch("redis.asyncio.from_url", return_value=fake_redis):
        backend = RedisStreamBackend(redis_url="redis://localhost:6379/0")
        await backend.connect()

        worker = StreamWorkerDaemon()

        # Telemetry event with high brute force failure count
        event = {
            "event_id": "stream-ev-101",
            "source_ip": "10.10.10.5",
            "destination_ip": "10.10.10.50",
            "destination_port": 445,
            "protocol": "TCP",
            "is_malicious": True,
            "attack_type": "Brute Force",
            "auth_failures": 8,
            "timestamp": "2026-08-20T10:00:00Z",
            "features": {
                "flow_duration": 120.0,
                "packet_length": 500
            }
        }

        # Process through worker
        res = await worker.process_telemetry_event(event)

        assert res["is_malicious"] is True
        assert res["correlation_bundle"] is not None
        assert res["correlation_bundle"]["event_count"] >= 1

        # Publish to incident stream
        msg_id = await backend.publish_event(
            stream_key="sentinel:incidents",
            event_data=res["correlation_bundle"]
        )
        assert msg_id is not None

        # Verify message exists in sentinel:incidents stream
        consumed = await backend.consume_events(
            stream_key="sentinel:incidents",
            group_name="sentinel:incident:testgroup",
            consumer_name="test-consumer-01",
            count=1,
            block_ms=1000
        )
        assert len(consumed) == 1
        assert consumed[0]["data"]["source_ip"] == "10.10.10.5"

        await backend.disconnect()
