"""
tests/unit/test_phase4_integrations.py
======================================
Unit tests for Phase 4 External Integration Connectors.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.integration_service import IntegrationService


@pytest.mark.asyncio
async def test_integration_notification_dispatcher():
    """Validates dispatch of critical incident alerts to active enterprise connectors."""
    db = AsyncMock()
    mock_integ1 = MagicMock()
    mock_integ1.name = "Slack SOC Alerts"
    mock_integ1.integration_type = "SLACK"
    mock_integ1.status = "ACTIVE"

    mock_res = MagicMock()
    mock_res.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_integ1])))
    db.execute = AsyncMock(return_value=mock_res)
    db.flush = AsyncMock()

    count = await IntegrationService.dispatch_notification(
        db=db,
        organization_id="org-prod",
        event_title="Critical Ransomware Outbreak Detected",
        event_body={"incident_id": "INC-999", "risk_score": 98.5}
    )

    assert count == 1
