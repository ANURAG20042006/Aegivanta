"""
tests/unit/test_investigation_timeline.py
=========================================
Phase 3.6 Unit Tests: Automated Investigation Timeline Service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.services.investigation_timeline_service import InvestigationTimelineService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_incident_investigation_timeline():
    """Verify chronological timeline reconstruction and summary statistics."""
    mock_inc = Incident(
        id="inc-tl-1",
        incident_code="INC-TL001",
        status="INVESTIGATING",
        severity="High",
        risk_score=72.0,
        attack_type="Brute Force",
        source_ip="192.168.1.5",
        destination_ip="10.0.0.1",
        analyst="analyst_jane",
        timestamp=datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc),
        first_seen=datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc),
        last_seen=datetime(2026, 8, 20, 10, 30, 0, tzinfo=timezone.utc)
    )

    mock_events = [
        IncidentTimelineEvent(
            id="tle-1",
            incident_id="inc-tl-1",
            timestamp=datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc),
            event_type="DETECTION",
            title="Initial Detection",
            description="Brute force attack pattern identified.",
            actor="CORRELATION_ENGINE"
        ),
        IncidentTimelineEvent(
            id="tle-2",
            incident_id="inc-tl-1",
            timestamp=datetime(2026, 8, 20, 10, 15, 0, tzinfo=timezone.utc),
            event_type="ANALYST_ACTION",
            title="Analyst Assigned",
            description="Assigned to analyst_jane",
            actor="analyst_jane"
        )
    ]

    mock_db = AsyncMock()
    # First query returns incident, second returns timeline events
    res_inc = MagicMock()
    res_inc.scalar_one_or_none.return_value = mock_inc
    res_tl = MagicMock()
    res_tl.scalars.return_value.all.return_value = mock_events

    mock_db.execute.side_effect = [res_inc, res_tl]

    res = await InvestigationTimelineService.get_incident_timeline("inc-tl-1", mock_db)

    assert "summary" in res
    assert "timeline" in res
    assert res["summary"]["incident_code"] == "INC-TL001"
    assert res["summary"]["total_timeline_entries"] == 2
    assert res["summary"]["assigned_analyst"] == "analyst_jane"
    assert len(res["timeline"]) == 2
    assert res["timeline"][0]["event_type"] == "DETECTION"
