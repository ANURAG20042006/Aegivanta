"""
tests/security/test_phase8_9_security.py
========================================
Security Tests for Phase 8 (Detection Rules) & Phase 9 (AI Security Copilot).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.ai_copilot_service import AICopilotService
from backend.app.core.exceptions import SentinelAIException


@pytest.mark.asyncio
async def test_copilot_cross_tenant_access_blocked():
    """Attempting to query Copilot for another tenant's incident must be rejected."""
    db = AsyncMock()
    # Incident belongs to ten-other, user belongs to ten-attacker
    res_none = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    db.execute = AsyncMock(return_value=res_none)

    with pytest.raises(SentinelAIException) as exc_info:
        await AICopilotService.analyze_incident(db, "inc-victim", "ten-attacker")
    assert exc_info.value.status_code == 404
