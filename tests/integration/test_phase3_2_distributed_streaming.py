"""
tests/integration/test_phase3_2_distributed_streaming.py
========================================================
Integration test verifying end-to-end distributed telemetry streaming pipeline:
Ingest -> Redis Stream -> Consumer Group -> ML Worker Inference -> XACK.
"""

import pytest
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend, DistributedStreamEngine
from backend.app.schemas.predict import PacketFeatureVector


@pytest.mark.asyncio
async def test_end_to_end_distributed_streaming_and_ack():
    """Verify full streaming lifecycle with worker consumption and acknowledgment."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    engine = DistributedStreamEngine(backend=backend)

    # 1. Ingest telemetry event
    flow_payload = {
        "event_id": "stream-flow-001",
        "source_ip": "198.51.100.77",
        "destination_ip": "10.0.0.1",
        "source_port": 50000,
        "destination_port": 80,
        "protocol": "TCP",
        "flow_duration": 10000.0,
        "total_fwd_packets": 5.0,
        "packet_length_mean": 400.0
    }
    ingest_res = await engine.ingest_event(flow_payload, stream_key="sentinel:telemetry")
    assert ingest_res["status"] == "QUEUED"
    msg_stream_id = ingest_res["stream_id"]

    # 2. Worker consumes event from consumer group
    msgs = await backend.consume_events(
        stream_key="sentinel:telemetry",
        group_name="sentinel:telemetry:group",
        consumer_name="worker-alpha",
        count=5
    )
    assert len(msgs) == 1
    consumed_msg = msgs[0]
    assert consumed_msg["id"] == msg_stream_id
    assert consumed_msg["data"]["source_ip"] == "198.51.100.77"

    # 3. Simulate successful worker ML processing and ACK
    ack_ok = await backend.acknowledge_event(
        stream_key="sentinel:telemetry",
        group_name="sentinel:telemetry:group",
        message_id=consumed_msg["id"]
    )
    assert ack_ok is True
    engine.metrics["acked_total"] += 1
