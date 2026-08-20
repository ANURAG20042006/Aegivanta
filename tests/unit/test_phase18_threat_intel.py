import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.threat_intelligence_platform_service import ThreatIntelligencePlatformService
from backend.app.models.threat_intel_platform import ThreatActor, ThreatCampaign
from backend.app.models.threat_intel import ThreatIndicator


@pytest.mark.asyncio
async def test_threat_actor_and_campaign_creation():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p18-actor"

        actor = ThreatActor(
            tenant_id=tenant_id,
            name="APT-99 CyberPhantom",
            aliases=["ShadowFox", "G0099"],
            actor_type="NATION_STATE",
            origin_country="RU",
            motivation="ESPIONAGE",
            sophistication="EXPERT",
            confidence_score=0.95,
            ttp_list=["T1059", "T1021", "T1110"]
        )
        db.add(actor)
        await db.flush()

        assert actor.id is not None
        assert actor.name == "APT-99 CyberPhantom"

        campaign = ThreatCampaign(
            tenant_id=tenant_id,
            name="Operation GhostNet Ingress",
            actor_id=actor.id,
            objective="Defense Network Infiltration",
            malware_families=["PhantomLoader", "DarkBeast"],
            targeted_sectors=["Defense", "Energy"],
            confidence=0.92,
            is_active=True
        )
        db.add(campaign)
        await db.flush()

        assert campaign.id is not None
        assert campaign.actor_id == actor.id


@pytest.mark.asyncio
async def test_indicator_sighting_and_hit_count_update():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p18-sight"

        # Create indicator
        indicator = ThreatIndicator(
            ioc_type="ipv4",
            raw_value="198.51.100.200",
            normalized_value="198.51.100.200",
            threat_type="c2",
            severity="HIGH",
            confidence=0.9,
            source="CISA_KNOWN_EXPLOITED",
            hit_count=0
        )
        db.add(indicator)
        await db.flush()

        # Record sighting
        sighting = await ThreatIntelligencePlatformService.record_sighting(
            db=db,
            tenant_id=tenant_id,
            indicator_id=indicator.id,
            source_ip="198.51.100.200",
            destination_ip="10.0.0.5"
        )

        assert sighting is not None
        assert sighting.is_confirmed_threat is True
        assert indicator.hit_count >= 1
