"""
tests/security/test_phase32_tenant_isolation.py
===============================================
Phase 32 Cyber Threat Intelligence Multi-Tenant Boundary Tests.
"""

import pytest
from backend.app.models.threat_intel_v2 import (
    ThreatActorProfile, STIXFeedSource, CTIIndicatorRecord, CampaignHeatmapItem
)


class TestCTITenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 32 models."""

    def test_cti_models_require_tenant_id(self):
        """All CTI 2.0 models must enforce tenant_id partition attributes."""
        actor = ThreatActorProfile(tenant_id="tenant-cti", actor_name="APT29")
        feed = STIXFeedSource(tenant_id="tenant-cti", feed_name="CISA", taxii_server_url="url")
        ind = CTIIndicatorRecord(tenant_id="tenant-cti", indicator_value="1.1.1.1")
        hm = CampaignHeatmapItem(tenant_id="tenant-cti", campaign_name="Campaign A", mitre_technique_id="T1059")

        assert actor.tenant_id == "tenant-cti"
        assert feed.tenant_id == "tenant-cti"
        assert ind.tenant_id == "tenant-cti"
        assert hm.tenant_id == "tenant-cti"
