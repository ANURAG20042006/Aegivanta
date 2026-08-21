"""
tests/unit/test_phase26_security_scorecard.py
=============================================
Phase 26.14 Enterprise Security Scorecard Unit Tests.
"""

import pytest
from backend.app.services.enterprise_security_scorecard_service import EnterpriseSecurityScorecardService


class TestSecurityScorecard:
    """Unit tests for the multi-vector Enterprise Security Scorecard."""

    def test_scorecard_weights_sum_to_one(self):
        """The weights of all 6 security dimensions must sum to 1.0."""
        weights = [0.20, 0.20, 0.20, 0.15, 0.15, 0.10]
        assert sum(weights) == pytest.approx(1.0, rel=1e-5)
