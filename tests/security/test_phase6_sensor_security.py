"""
tests/security/test_phase6_sensor_security.py
=============================================
Phase 6 Security Tests: Sensor Token Authentication, Expiration, and Revocation Enforcement.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.sensor_service import SensorService
from backend.app.core.exceptions import AuthenticationError


@pytest.mark.asyncio
async def test_invalid_sensor_token_rejected():
    """Heartbeat with incorrect token hash must fail with AuthenticationError."""
    db = AsyncMock()
    mock_sensor = MagicMock()
    mock_sensor.status = "ONLINE"
    mock_sensor.enrollment_token_hash = "correct_hash"
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_sensor)))

    with pytest.raises(AuthenticationError, match="Invalid sensor enrollment credentials"):
        await SensorService.process_heartbeat(db, "sen-123", "wrong_token_123")
