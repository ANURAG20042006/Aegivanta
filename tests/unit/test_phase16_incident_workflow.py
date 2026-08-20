"""
tests/unit/test_phase16_incident_workflow.py
============================================
Phase 16.4 & 16.5 Unit Tests: Incident State Machine & Immutable Timeline.
"""

import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.models.incident import Incident
from backend.app.services.incident_workflow_service import IncidentWorkflowService
from backend.app.core.exceptions import SentinelAIException


@pytest.mark.asyncio
async def test_incident_status_transition_and_timeline():
    """Validates audited lifecycle transitions and immutable timeline event creation."""
    await init_db()
    async with AsyncSessionFactory() as db:
        incident = Incident(
            title="Suspicious Network Intrusion",
            source_ip="198.51.100.5",
            destination_ip="10.0.0.12",
            source_port=54321,
            destination_port=443,
            protocol="TCP",
            packet_length=1500,
            attack_type="DDoS",
            is_malicious=True,
            severity="High",
            status="DETECTED"
        )
        db.add(incident)
        await db.flush()

        # Valid transition: DETECTED -> TRIAGED
        updated = await IncidentWorkflowService.transition_incident_status(
            db=db,
            incident_id=incident.id,
            new_status="TRIAGED",
            actor="analyst_alice",
            reason="Confirmed anomaly signature",
            notes="Initial triage completed, escalating to investigation."
        )
        assert updated.status == "TRIAGED"
        assert updated.triaged_at is not None
        assert "analyst_alice" in updated.notes

        # Assign analyst
        assigned = await IncidentWorkflowService.assign_incident_analyst(
            db=db,
            incident_id=incident.id,
            analyst_username="lead_analyst_bob",
            actor="analyst_alice"
        )
        assert assigned.analyst == "lead_analyst_bob"

        # Check Timeline
        timeline = await IncidentWorkflowService.get_incident_timeline(db, incident.id)
        assert len(timeline) >= 2
        types = [t["event_type"] for t in timeline]
        assert "STATUS_CHANGE" in types
        assert "ANALYST_ASSIGNMENT" in types


@pytest.mark.asyncio
async def test_invalid_status_transition_raises_error():
    """Validates fail-closed state machine behavior on illegal transitions."""
    await init_db()
    async with AsyncSessionFactory() as db:
        incident = Incident(
            title="Minor Port Scan",
            source_ip="198.51.100.7",
            destination_ip="10.0.0.14",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            packet_length=64,
            attack_type="PortScan",
            is_malicious=True,
            severity="Low",
            status="NEW"
        )
        db.add(incident)
        await db.flush()

        # Illegal transition: NEW -> RESOLVED without triage/containment
        with pytest.raises(SentinelAIException) as exc_info:
            await IncidentWorkflowService.transition_incident_status(
                db=db,
                incident_id=incident.id,
                new_status="RESOLVED",
                actor="analyst_alice"
            )
        assert exc_info.value.status_code == 400
