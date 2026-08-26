"""
tests/unit/test_phase48_adversarial_service.py
==============================================
Unit tests for AdversarialDefenseService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.adversarial_defense_service import AdversarialDefenseService
from backend.app.models.ai_ml_model_platform import AdversarialAttackEvent


@pytest.mark.asyncio
async def test_get_defense_summary():
    db = AsyncMock()
    mock_event = AdversarialAttackEvent(
        id="evt-1",
        tenant_id="tenant-ml-test",
        model_id="cat-001",
        model_name="CatBoost-ThreatClassifier",
        attack_type="EVASION",
        attack_severity="HIGH",
        confidence_score=0.96,
        defense_mechanism="ADVERSARIAL_INPUT_DETECTION",
        blocked=True,
        defense_latency_ms=1.1
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_event]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    summary = await AdversarialDefenseService.get_defense_summary(db=db, tenant_id="tenant-ml-test")
    assert summary["adversarial_defense_score"] >= 95.0
    assert summary["block_rate"] == 1.0
    assert summary["total_attacks_detected_30d"] == 1
    assert summary["total_attacks_blocked_30d"] == 1
    assert "EVASION" in summary["attack_type_breakdown"]
    assert len(summary["defense_mechanisms_active"]) >= 3



@pytest.mark.asyncio
async def test_simulate_defense():
    db = AsyncMock()
    sim = await AdversarialDefenseService.simulate_defense(
        db=db,
        tenant_id="tenant-ml-test",
        model_id="cat-001",
        attack_type="MODEL_EXTRACTION",
        attack_payload={"query_count": 50000}
    )
    assert sim["attack_type"] == "MODEL_EXTRACTION"
    assert sim["blocked"] is True
    assert sim["outcome"] == "ATTACK_BLOCKED"
    assert sim["confidence_score"] == 0.95
    assert sim["defense_mechanism"] == "ADVERSARIAL_INPUT_DETECTION"


@pytest.mark.asyncio
async def test_list_attack_events_with_mock():
    db = AsyncMock()
    mock_event = AdversarialAttackEvent(
        id="evt-1",
        tenant_id="tenant-ml-test",
        model_id="cat-001",
        model_name="CatBoost-ThreatClassifier",
        attack_type="EVASION",
        attack_severity="HIGH",
        confidence_score=0.96,
        defense_mechanism="ADVERSARIAL_INPUT_DETECTION",
        blocked=True,
        defense_latency_ms=1.1
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_event]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    events = await AdversarialDefenseService.list_attack_events(db=db, tenant_id="tenant-ml-test")
    assert isinstance(events, list)
    assert len(events) >= 1
    assert events[0]["attack_type"] == "EVASION"
    assert events[0]["blocked"] is True
