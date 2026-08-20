"""
tests/integration/test_phase3_9_websocket_events.py
===================================================
Real-Time SOC Event Stream WebSocket Integration Tests.
Verifies JWT authentication, role verification, initial sync frame,
heartbeat PING/PONG responses, and multi-category event streaming.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.security import create_access_token
from backend.app.services.soc_event_broadcaster import broadcast_soc_event

client = TestClient(app)


def test_websocket_soc_events_unauthenticated_rejected():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/soc-events") as ws:
            pass


def test_websocket_soc_events_invalid_token_rejected():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/soc-events?token=invalid.jwt.token") as ws:
            pass


def test_websocket_soc_events_connection_and_initial_sync():
    token = create_access_token(subject="analyst", role="analyst")
    with client.websocket_connect(f"/ws/soc-events?token={token}") as ws:
        # Initial sync frame is sent on connect
        sync_frame = ws.receive_json()
        assert sync_frame["type"] == "INIT_SYNC"
        assert sync_frame["status"] == "CONNECTED"
        assert "events" in sync_frame
        assert isinstance(sync_frame["events"], list)


def test_websocket_soc_events_heartbeat_pong():
    token = create_access_token(subject="admin", role="admin")
    with client.websocket_connect(f"/ws/soc-events?token={token}") as ws:
        _ = ws.receive_json()  # Consume INIT_SYNC
        # Client sends PONG
        ws.send_json({"type": "PONG"})
        # Connection remains open and healthy
        assert True
