"""
tests/unit/test_incident_service.py
===================================
Phase 3.6 Unit Tests: Incident Aggregation, Deduplication, and Lifecycle Transitions.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from backend.app.models.incident import Incident, is_valid_state_transition
from backend.app.services.incident_service import IncidentService


@pytest.mark.unit
def test_state_machine_valid_and_invalid_transitions():
    """Verify state transition rules for incident lifecycle."""
    # Valid transitions
    assert is_valid_state_transition("OPEN", "INVESTIGATING") is True
    assert is_valid_state_transition("OPEN", "TRIAGED") is True
    assert is_valid_state_transition("INVESTIGATING", "CONTAINED") is True
    assert is_valid_state_transition("INVESTIGATING", "RESOLVED") is True
    assert is_valid_state_transition("CONTAINED", "RESOLVED") is True
    assert is_valid_state_transition("RESOLVED", "CLOSED") is True
    assert is_valid_state_transition("OPEN", "OPEN") is True

    # Invalid transitions
    assert is_valid_state_transition("DETECTED", "CLOSED") is False
    assert is_valid_state_transition("DETECTED", "RESOLVED") is False
    assert is_valid_state_transition("RESOLVED", "TRIAGED") is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_incident_from_correlation():
    """Verify creation of a new Incident from a correlation bundle."""
    bundle = {
        "correlation_id": "CORR-TEST-001",
        "source_ip": "10.0.0.99",
        "destination_ip": "10.0.0.1",
        "attack_type": "Brute Force",
        "severity": "High",
        "risk_score": 78.5,
        "confidence": 0.92,
        "event_count": 3,
        "detection_reason": "Brute force attack on authentication port."
    }

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()

    # Mock search returning None (no existing incident)
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    inc, is_new = await IncidentService.create_or_update_from_correlation(bundle, mock_db)

    assert is_new is True
    assert inc.source_ip == "10.0.0.99"
    assert inc.status == "OPEN"
    assert inc.risk_score == 78.5
    assert inc.alert_count == 3
    assert mock_db.add.call_count >= 2  # Added incident + timeline entry


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aggregate_into_existing_incident():
    """Verify deduplication aggregates into existing active incident."""
    existing_inc = Incident(
        id="inc-exist-1",
        incident_code="INC-EXIST01",
        alert_id="ALT-001",
        status="OPEN",
        severity="Medium",
        risk_score=50.0,
        alert_count=2,
        source_ip="10.0.0.50",
        destination_ip="10.0.0.1",
        source_port=1234,
        destination_port=80,
        protocol="TCP",
        packet_length=500,
        attack_type="PortScan",
        is_malicious=True
    )

    bundle = {
        "correlation_id": "CORR-TEST-002",
        "source_ip": "10.0.0.50",
        "destination_ip": "10.0.0.1",
        "attack_type": "Brute Force",
        "severity": "High",
        "risk_score": 75.0,
        "event_count": 4,
        "detection_reason": "Aggregated subsequent brute force flow."
    }

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = existing_inc
    mock_db.execute.return_value = mock_res

    inc, is_new = await IncidentService.create_or_update_from_correlation(bundle, mock_db)

    assert is_new is False
    assert inc.id == "inc-exist-1"
    assert inc.alert_count == 6  # 2 + 4
    assert inc.severity == "High"  # Elevated from Medium
    assert inc.risk_score == 75.0  # Elevated from 50.0
