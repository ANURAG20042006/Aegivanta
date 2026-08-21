"""
tests/unit/test_phase34_epss_feed.py
====================================
Phase 34 EPSS 2.0 Distribution & CISA KEV Sync Unit Tests.
"""

import pytest
from backend.app.services.epss_feed_service import EPSSFeedService


class TestEPSSFeed:
    """Unit tests for EPSS probability distribution buckets."""

    def test_epss_distribution_buckets_exist(self):
        """EPSSFeedService must return 5 statistical probability buckets."""
        buckets = EPSSFeedService.get_epss_distribution_buckets()
        assert len(buckets) == 5
        assert any("0.90" in b["bucket"] for b in buckets)
