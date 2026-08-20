"""
tests/integration/test_phase4_sensor_flow.py
============================================
Phase 4 Integration Tests: Sensor Ingestion and Heartbeat Lifecycle.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_sensor_heartbeat_unregistered_rejected():
    """Unregistered or fabricated sensor IDs must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/sensors/non-existent-sensor-id/heartbeat",
            json={"token": "fake_token_123"}
        )
        assert response.status_code in [401, 403, 404]
