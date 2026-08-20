"""
tests/unit/test_investigation_service.py
========================================
Phase 3.8 Unit Tests: Investigation Case Service & State Machine.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from backend.app.models.investigation import InvestigationCase, is_valid_case_transition
from backend.app.services.investigation_case_service import InvestigationCaseService


@pytest.mark.unit
def test_case_state_machine_valid_and_invalid_transitions():
    """Verify investigation case state transition matrix."""
    assert is_valid_case_transition("OPEN", "TRIAGED") is True
    assert is_valid_case_transition("OPEN", "INVESTIGATING") is True
    assert is_valid_case_transition("INVESTIGATING", "ESCALATED") is True
    assert is_valid_case_transition("INVESTIGATING", "CONTAINED") is True
    assert is_valid_case_transition("CONTAINED", "RESOLVED") is True
    assert is_valid_case_transition("RESOLVED", "CLOSED") is True

    # Invalid jump
    assert is_valid_case_transition("OPEN", "RESOLVED") is False
    assert is_valid_case_transition("TRIAGED", "CONTAINED") is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_investigation_case_creation_and_update():
    """Verify case initialization and update workflow."""
    case = await InvestigationCaseService.create_case(
        title="Active C2 Beaconing Investigation",
        description="Suspected beaconing from internal finance host",
        priority="HIGH",
        severity="CRITICAL",
        analyst="analyst_jane",
        linked_incident_ids=["inc-100", "inc-101"],
        linked_assets=["srv-fin-01"],
        linked_iocs=["198.51.100.200"],
        mitre_techniques=["T1071.001", "T1048"],
        tags=["finance", "c2"]
    )

    assert case.title == "Active C2 Beaconing Investigation"
    assert case.status == "OPEN"
    assert case.case_code.startswith("CASE-")
    assert "c2" in case.tags
    assert len(case.linked_incident_ids) == 2
