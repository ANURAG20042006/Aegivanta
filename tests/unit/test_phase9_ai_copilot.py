"""
tests/unit/test_phase9_ai_copilot.py
====================================
Unit tests for AI Security Copilot: Incident Explanation, Attack Path, and Secret Sanitization.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.ai_copilot_service import AICopilotService
from backend.app.models.incident import Incident
from backend.app.models.alert import Alert


def test_sanitize_context_secrets_redaction():
    """Validates that JWT tokens, sensor keys, API keys, and passwords are fully redacted."""
    raw_prompt = (
        "Analyst query: Check telemetry for token sen_112233445566778899aabbccddeeff001122334455667788 "
        "and user password: SecretPassword123! with api key ak_live_abcdef1234567890abcdef1234567890"
    )
    sanitized = AICopilotService.sanitize_context(raw_prompt)
    assert "sen_1122" not in sanitized
    assert "[REDACTED_SENSOR_TOKEN]" in sanitized
    assert "SecretPassword123!" not in sanitized
    assert "ak_live" not in sanitized


@pytest.mark.asyncio
async def test_copilot_incident_explanation():
    """Validates structured explainable analysis for a detected incident."""
    db = AsyncMock()
    mock_incident = Incident(
        id="inc-999",
        title="Distributed Port Scan & SSH Brute Force",
        severity="HIGH",
        risk_score=88
    )

    mock_alert = Alert(
        id="alt-1",
        alert_id="ALT-12345",
        incident_id="inc-999",
        title="SSH Brute Force",
        attack_type="SSH_BRUTE_FORCE",
        source_ip="192.168.1.50",
        destination_ip="10.0.0.10"
    )


    res_inc = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_incident))
    res_alt = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_alert]))))

    db.execute = AsyncMock(side_effect=[res_inc, res_alt])

    result = await AICopilotService.analyze_incident(db, "inc-999", "ten-prod")

    assert result["incident_id"] == "inc-999"
    assert result["risk_score"] == 88
    assert len(result["why_detected"]) > 0
    assert len(result["attack_path"]) > 0
    assert len(result["response_proposals"]) > 0
    assert result["response_proposals"][0]["requires_approval"] is True
