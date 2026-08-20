"""
tests/unit/test_mitre_detection_coverage.py
===========================================
Phase 3.6 Unit Tests: MITRE ATT&CK Detection Coverage Analytics.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.mitre_coverage_service import MitreCoverageService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mitre_coverage_calculation():
    """Verify matrix coverage calculation against active detection rules."""
    mock_db = AsyncMock()
    res = MagicMock()
    res.scalars.return_value.all.return_value = [
        {"mitre_techniques": ["T1110.001", "T1021.002"]},
        {"mitre_techniques": ["T1110.001", "T1071.001"]}
    ]
    mock_db.execute.return_value = res

    analytics = await MitreCoverageService.get_coverage_analytics(mock_db)

    assert analytics["total_catalog_techniques"] > 20
    assert analytics["covered_techniques_count"] >= 10
    assert analytics["coverage_percentage"] > 30.0
    assert len(analytics["covered_techniques"]) >= 10
    assert len(analytics["highest_frequency_detected"]) >= 1
    assert "technique_id" in analytics["covered_techniques"][0]
