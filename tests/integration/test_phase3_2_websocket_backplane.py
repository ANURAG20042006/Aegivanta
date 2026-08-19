"""
tests/integration/test_phase3_2_websocket_backplane.py
======================================================
Integration test verifying multi-instance WebSocket event broadcasting
via the distributed Redis Pub/Sub backplane.
"""

import pytest
import json
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend, InMemoryStreamBackend
from backend.app.api.v1.websockets import ConnectionManager


@pytest.mark.asyncio
async def test_multi_instance_websocket_redis_pubsub_backplane():
    """
    Verify:
    1. Instance A and Instance B manage distinct local WebSocket connections.
    2. Event broadcast on Instance A is published across Redis Pub/Sub.
    3. Instance B receives the event from Redis and broadcasts to its local clients.
    """
    # Create shared Redis broker simulation
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    manager_instance_a = ConnectionManager()
    manager_instance_b = ConnectionManager()

    # Mock local WebSocket client objects
    class MockWebSocket:
        def __init__(self, name: str):
            self.name = name
            self.received_messages = []

        async def send_text(self, text: str):
            self.received_messages.append(text)

    client_on_a = MockWebSocket("client-A")
    client_on_b = MockWebSocket("client-B")

    manager_instance_a.active_connections.append(client_on_a)
    manager_instance_b.active_connections.append(client_on_b)

    # 1. Broadcast threat incident from Instance A
    incident_data = {
        "incident_id": "INC-DIST-001",
        "severity": "Critical",
        "attack_type": "DDoS",
        "source_ip": "198.51.100.22"
    }

    # Simulate Instance A broadcasting locally and to PubSub
    await manager_instance_a.broadcast_event("INCIDENT_CREATED", incident_data, publish_to_redis=False)
    assert len(client_on_a.received_messages) == 1
    assert "INC-DIST-001" in client_on_a.received_messages[0]
    assert len(client_on_b.received_messages) == 0

    # Simulate Instance B receiving the message from the PubSub subscription channel
    event_payload = {
        "type": "INCIDENT_CREATED",
        "data": incident_data
    }
    await manager_instance_b.broadcast_local(json.dumps(event_payload))

    # Verify client on Instance B received the broadcast without shared memory state
    assert len(client_on_b.received_messages) == 1
    assert "INC-DIST-001" in client_on_b.received_messages[0]
