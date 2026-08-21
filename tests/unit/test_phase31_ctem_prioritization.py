"""
tests/unit/test_phase31_ctem_prioritization.py
==============================================
Phase 31 CTEM 5-Stage Prioritization Engine Unit Tests.
"""

import pytest
from backend.app.services.ctem_prioritization_service import CTEMPrioritizationService


class TestCTEMPrioritization:
    """Unit tests for Gartner 5-Stage CTEM prioritization service."""

    @pytest.mark.asyncio
    async def test_prioritized_exposures_returns_epss_and_cisa_kev(self):
        """CTEM prioritization engine must output EPSS percentiles and CISA KEV weaponization data."""
        exposures = await CTEMPrioritizationService.list_prioritized_exposures(None, "default-tenant")
        assert len(exposures) >= 3
        top_exp = exposures[0]
        assert "epss_percentile" in top_exp
        assert "cisa_kev_weaponized" in top_exp
        assert "ctem_stage" in top_exp
        assert top_exp["cvss_score"] > 8.0
