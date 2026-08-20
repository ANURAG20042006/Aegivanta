"""
tests/unit/test_phase5_posture.py
=================================
Unit tests for Phase 5 Security Posture Score Calculation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.security_posture_service import SecurityPostureService


@pytest.mark.asyncio
async def test_security_posture_calculation():
    """Validates computation of 0-100 explainable posture score and dimension scores."""
    db = AsyncMock()

    # Mock empty/standard returns
    mock_res_empty = MagicMock()
    mock_res_empty.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    mock_res_empty.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(return_value=mock_res_empty)

    result = await SecurityPostureService.calculate_posture(db, "org-acme-123")

    assert "overall_posture_score" in result
    assert 0 <= result["overall_posture_score"] <= 100
    assert "dimension_scores" in result
    assert "identity_security" in result["dimension_scores"]
    assert "api_security" in result["dimension_scores"]
    assert "recommendations" in result
