"""
tests/unit/test_phase39_horizon_indicators.py
=============================================
Phase 39 Threat Horizon Indicator Unit Tests.
"""

import pytest
from backend.app.models.predictive_intel import ThreatHorizonIndicator


class TestHorizonIndicators:
    """Unit tests for ThreatHorizonIndicator model."""

    def test_horizon_indicator_model(self):
        """ThreatHorizonIndicator must store name, category, trend, and global sightings count."""
        ind = ThreatHorizonIndicator(
            tenant_id="tenant-pred",
            indicator_name="Ransomware Surge",
            category="RANSOMWARE_CAMPAIGN",
            trajectory_trend="SURGING",
            observed_global_sightings=6820
        )
        assert ind.indicator_name == "Ransomware Surge"
        assert ind.trajectory_trend == "SURGING"
        assert ind.observed_global_sightings == 6820
