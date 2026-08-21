"""
tests/unit/test_phase32_ioc_decay.py
====================================
Phase 32 Dynamic IOC Sighting & Time Decay Unit Tests.
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.app.services.ioc_decay_service import IOCDecayService


class TestIOCDecay:
    """Unit tests for exponential IOC confidence decay calculations."""

    def test_exponential_decay_halflife(self):
        """Confidence score must halve after one exact halflife period."""
        initial_score = 100.0
        past_time = datetime.now(timezone.utc) - timedelta(days=45)
        decayed = IOCDecayService.calculate_decayed_score(
            initial_score=initial_score,
            last_sighted_at=past_time,
            halflife_days=45
        )
        assert decayed == 50.0

    def test_recent_sighting_retains_high_confidence(self):
        """Indicators seen very recently must retain nearly 100% confidence."""
        initial_score = 95.0
        recent_time = datetime.now(timezone.utc) - timedelta(hours=2)
        decayed = IOCDecayService.calculate_decayed_score(
            initial_score=initial_score,
            last_sighted_at=recent_time,
            halflife_days=45
        )
        assert decayed >= 94.0
