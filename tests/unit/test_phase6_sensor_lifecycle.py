"""
tests/unit/test_phase6_sensor_lifecycle.py
==========================================
Unit tests for Phase 6 Sensor Token Rotation, OTA Upgrades & Fleet Health.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.sensor_service import SensorService
from backend.app.models.sensor import Sensor


@pytest.mark.asyncio
async def test_sensor_token_rotation():
    """Validates generation and hashing of new cryptographic enrollment tokens."""
    db = AsyncMock()
    mock_sensor = Sensor(
        id="sen-123",
        tenant_id="ten-prod",
        name="K8s Agent",
        hostname="node-01",
        ip_address="10.0.0.1",
        os_type="linux",
        status="ONLINE",
        enrollment_token_hash="old_hash"
    )
    mock_res = MagicMock()
    mock_res.scalar_one_or_none = MagicMock(return_value=mock_sensor)
    db.execute = AsyncMock(return_value=mock_res)
    db.flush = AsyncMock()

    sensor, new_token = await SensorService.rotate_token(db, "sen-123", "ten-prod")

    assert new_token.startswith("sen_")
    assert sensor.enrollment_token_hash == SensorService._hash_token(new_token)
    assert sensor.token_expires_at is not None


@pytest.mark.asyncio
async def test_fleet_health_calculation():
    """Validates computation of fleet health index and offline sensors."""
    from datetime import datetime, timezone
    db = AsyncMock()
    now = datetime.now(timezone.utc)
    mock_s1 = Sensor(status="ONLINE", health_score=95, offline_buffer_events=0, last_heartbeat=now)
    mock_s2 = Sensor(status="ONLINE", health_score=60, offline_buffer_events=1200, last_heartbeat=now)

    # Mock list_sensors
    SensorService.list_sensors = AsyncMock(return_value=[mock_s1, mock_s2])

    health = await SensorService.get_fleet_health(db, "ten-prod")
    assert health["total_sensors"] == 2
    assert "average_health_score" in health
    assert health["total_buffered_events"] == 1200

