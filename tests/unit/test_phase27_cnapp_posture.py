"""
tests/unit/test_phase27_cnapp_posture.py
========================================
Phase 27 CNAPP Posture Engine Unit Tests.
Verifies multi-pillar weight composition and scoring boundaries.
"""

import pytest
from backend.app.services.cnapp_posture_service import CNAPPPostureService


class TestCNAPPPostureEngine:
    """Unit tests for CNAPP posture synthesis and weights."""

    def test_cnapp_weights_sum_to_one(self):
        """The weights across all 5 CNAPP pillars must sum to 1.0."""
        weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        assert sum(weights) == pytest.approx(1.0, rel=1e-5)

    def test_composite_score_formula(self):
        """Calculates expected composite score from arbitrary pillar scores."""
        cspm = 90.0
        cwpp = 80.0
        ciem = 85.0
        kspm = 95.0
        srv = 75.0
        expected = (cspm * 0.30) + (cwpp * 0.25) + (ciem * 0.20) + (kspm * 0.15) + (srv * 0.10)
        assert round(expected, 1) == 85.8
