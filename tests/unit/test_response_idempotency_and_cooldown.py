"""
tests/unit/test_response_idempotency_and_cooldown.py
====================================================
Phase 3.7 Unit Tests: Response Idempotency & Cooldown Rate Limiting.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from backend.app.models.response import ResponseActionRecord, IdempotencyRecord
from backend.app.models.incident import Incident
from backend.app.services.response_orchestrator import ResponseOrchestrator


@pytest.mark.unit
@pytest.mark.asyncio
async def test_idempotency_key_deduplication():
    """Verify identical request with same idempotency key returns existing record without duplicate execution."""
    existing_act = ResponseActionRecord(
        id="act-exist-01",
        incident_id="inc-test-01",
        action_type="BLOCK_IP",
        target_entity="198.51.100.1",
        status="SUCCEEDED",
        idempotency_key="idem-key-12345"
    )

    existing_idem = IdempotencyRecord(
        idempotency_key="idem-key-12345",
        action_id="act-exist-01",
        incident_id="inc-test-01",
        action_type="BLOCK_IP",
        target_entity="198.51.100.1"
    )

    mock_db = MagicMock()
    # 1st query: find idempotency record
    res_idem = MagicMock()
    res_idem.scalar_one_or_none.return_value = existing_idem
    # 2nd query: find action record
    res_act = MagicMock()
    res_act.scalar_one_or_none.return_value = existing_act

    mock_db.execute = AsyncMock(side_effect=[res_idem, res_act])

    act = await ResponseOrchestrator.submit_action(
        incident_id="inc-test-01",
        action_type="BLOCK_IP",
        target_entity="198.51.100.1",
        requested_by="admin",
        actor_role="admin",
        idempotency_key="idem-key-12345",
        db=mock_db
    )

    assert act.id == "act-exist-01"
    assert act.status == "SUCCEEDED"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cooldown_rejection_on_repeated_action():
    """Verify action requested within cooldown window is rejected."""
    mock_inc = Incident(
        id="inc-test-02",
        incident_code="INC-002",
        alert_id="ALT-002",
        status="OPEN",
        severity="HIGH",
        risk_score=75.0,
        source_ip="10.0.0.99",
        destination_ip="10.0.0.1",
        attack_type="PortScan",
        is_malicious=True
    )

    recent_act = ResponseActionRecord(
        id="act-recent-01",
        incident_id="inc-test-02",
        action_type="BLOCK_IP",
        target_entity="10.0.0.99",
        status="SUCCEEDED",
        created_at=datetime.now(timezone.utc) - timedelta(seconds=30)  # within 180s cooldown
    )

    mock_db = MagicMock()
    # 1st query: idempotency check (None)
    res_idem = MagicMock()
    res_idem.scalar_one_or_none.return_value = None
    # 2nd query: incident lookup
    res_inc = MagicMock()
    res_inc.scalar_one_or_none.return_value = mock_inc
    # 3rd query: policy lookup
    res_pol = MagicMock()
    res_pol.scalars().all.return_value = []
    # 4th query: recent action lookup (Found!)
    res_recent = MagicMock()
    res_recent.scalar_one_or_none.return_value = recent_act

    mock_db.execute = AsyncMock(side_effect=[res_idem, res_inc, res_pol, res_recent])

    with pytest.raises(ValueError, match="cooldown"):
        await ResponseOrchestrator.submit_action(
            incident_id="inc-test-02",
            action_type="BLOCK_IP",
            target_entity="10.0.0.99",
            requested_by="admin",
            actor_role="admin",
            idempotency_key="new-key-999",
            db=mock_db
        )
