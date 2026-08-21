"""
tests/security/test_phase32_feed_tamper_defense.py
==================================================
Phase 32 CTI Feed Integrity & Confidence Sanitization Security Tests.
"""

import pytest
from backend.app.services.ioc_decay_service import IOCDecayService


class TestFeedTamperDefense:
    """Security tests verifying decayed confidence bounds and anti-tamper safeguards."""

    def test_decayed_score_never_exceeds_initial_confidence(self):
        """Calculated decayed score must never exceed the initial verified score."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        score = IOCDecayService.calculate_decayed_score(90.0, now, 45)
        assert score <= 90.0
        assert score >= 0.0
