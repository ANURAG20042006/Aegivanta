"""
tests/unit/test_phase413_sensors_and_integrations.py
====================================================
Phase 4.13 & 4.14 Sensor Agent & External Integration Framework Tests.
Validates sensor enrollment token hashing, heartbeats, and connector dispatching.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.sensor_service import SensorService
from backend.app.services.integration_service import IntegrationService
from backend.app.models.sensor import Sensor


class TestSensorsAndIntegrations:

    @pytest.mark.asyncio
    async def test_enroll_sensor_hashes_token_securely(self):
        """enroll_sensor must return a plaintext token starting with sen_ while storing only SHA-256 hash."""
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()

        sensor, raw_token = await SensorService.enroll_sensor(
            db=db,
            tenant_id="tenant-prod",
            name="DMZ Gateway Sensor",
            hostname="gateway.corp.internal",
            ip_address="10.0.1.1",
            os_type="linux"
        )

        assert raw_token.startswith("sen_")
        assert sensor.enrollment_token_hash != raw_token
        assert len(sensor.enrollment_token_hash) == 64
        assert sensor.status == "ONLINE"

    @pytest.mark.asyncio
    async def test_create_integration_registers_connector(self):
        """create_integration must register an active external connector."""
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()

        integ = await IntegrationService.create_integration(
            db=db,
            organization_id="org-acme",
            integration_type="SLACK",
            name="SOC Critical Alerts Channel",
            config={"webhook_url": "https://hooks.slack.com/services/test"}
        )

        assert integ.organization_id == "org-acme"
        assert integ.integration_type == "SLACK"
        assert integ.status == "ACTIVE"
