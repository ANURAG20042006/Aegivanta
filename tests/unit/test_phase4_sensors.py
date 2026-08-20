"""
tests/unit/test_phase4_sensors.py
=================================
Unit tests for Phase 4 Telemetry Sensor Fleet Management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.sensor_service import SensorService
from backend.app.core.exceptions import AuthenticationError


@pytest.mark.asyncio
async def test_sensor_revocation_lifecycle():
    """Revoked sensor cannot send heartbeats or stream telemetry."""
    db = AsyncMock()
    # Mock finding a revoked sensor
    mock_sensor = MagicMock()
    mock_sensor.status = "REVOKED"
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_sensor)))

    with pytest.raises(AuthenticationError, match="revoked"):
        await SensorService.process_heartbeat(db, "sensor-123", "bad_or_revoked_token")
