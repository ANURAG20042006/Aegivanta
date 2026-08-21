"""
tests/unit/test_phase32_threat_actors.py
========================================
Phase 32 Threat Actor Profiling & Diamond Model Unit Tests.
"""

import pytest
from backend.app.models.threat_intel_v2 import ThreatActorProfile, CampaignHeatmapItem


class TestThreatActorProfiles:
    """Unit tests for threat actor profiles and Diamond Model attribution schemas."""

    def test_threat_actor_profile_model(self):
        """ThreatActorProfile must store Diamond Model attributes and MITRE techniques."""
        actor = ThreatActorProfile(
            tenant_id="tenant-123",
            actor_name="Volt Typhoon",
            aliases=["BRONZE SILHOUETTE"],
            country_of_origin="China",
            actor_type="NATION_STATE",
            primary_motivation="Pre-Positioning in Critical Infrastructure",
            sophistication_level="STRATEGIC",
            diamond_adversary="PLA Strategic Support Force",
            diamond_capability="Living-off-the-Land (LotL), WMI",
            diamond_infrastructure="Compromised SOHO Routers",
            diamond_victimology="Energy, Water, Telecom",
            targeted_sectors=["Energy", "Water"],
            primary_mitre_techniques=["T1059.001", "T1047"]
        )
        assert actor.actor_name == "Volt Typhoon"
        assert actor.diamond_adversary == "PLA Strategic Support Force"
        assert "T1059.001" in actor.primary_mitre_techniques

    def test_campaign_heatmap_model(self):
        """CampaignHeatmapItem must store heat level and confidence."""
        hm = CampaignHeatmapItem(
            tenant_id="tenant-123",
            campaign_name="Midnight Blizzard Infiltration",
            threat_actor="APT29",
            tactic_name="Initial Access",
            mitre_technique_id="T1195.002",
            technique_name="Supply Chain Compromise",
            heat_level=5,
            confidence_score=98.0
        )
        assert hm.heat_level == 5
        assert hm.mitre_technique_id == "T1195.002"
