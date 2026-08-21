"""
tests/unit/test_phase32_stix_taxii.py
=====================================
Phase 32 STIX 2.1 & TAXII 2.1 Engine Unit Tests.
"""

import pytest
from backend.app.models.threat_intel_v2 import STIXFeedSource


class TestSTIXTAXIIEngine:
    """Unit tests for STIX/TAXII threat feed subscription models."""

    def test_stix_feed_model_initialization(self):
        """STIXFeedSource model must store feed URL, collection ID, and format."""
        feed = STIXFeedSource(
            tenant_id="tenant-123",
            feed_name="CISA Automated Indicator Sharing (AIS)",
            taxii_server_url="https://taxii.cisa.dhs.gov/taxii2/",
            collection_id="cisa-ais-indicators",
            feed_format="STIX_2_1",
            poll_interval_minutes=30,
            feed_reputation_score=98.0,
            auto_ingest_enabled=True,
            total_indicators_ingested=18500,
            last_poll_status="SUCCESS"
        )
        assert feed.feed_name == "CISA Automated Indicator Sharing (AIS)"
        assert feed.feed_format == "STIX_2_1"
        assert feed.poll_interval_minutes == 30
        assert feed.total_indicators_ingested == 18500
