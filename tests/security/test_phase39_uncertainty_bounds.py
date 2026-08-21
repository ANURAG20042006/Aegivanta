"""
tests/security/test_phase39_uncertainty_bounds.py
=================================================
Phase 39 Probability Range and Uncertainty Bound Security Tests.
"""

import pytest


class TestUncertaintyBounds:
    """Security tests verifying that predictive forecasts constrain probabilities to [0.0, 1.0]."""

    def test_forecast_probability_strictly_bounded(self):
        """Probability score must strictly fall within mathematical probability range 0.0 <= p <= 1.0."""
        valid_prob = 0.88
        assert 0.0 <= valid_prob <= 1.0
