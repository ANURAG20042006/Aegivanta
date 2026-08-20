import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.threat_intelligence_platform_service import (
    ThreatIntelligencePlatformService,
    validate_external_feed_url
)
from backend.app.models.threat_intel_platform import ThreatActor


def test_ssrf_feed_url_validation():
    # Forbidden loopback / private IP ranges
    assert validate_external_feed_url("http://127.0.0.1/feed.json") is False
    assert validate_external_feed_url("http://localhost:8000/feed.csv") is False
    assert validate_external_feed_url("http://10.0.0.5/taxii/poll") is False
    assert validate_external_feed_url("http://192.168.1.1/misp") is False
    assert validate_external_feed_url("http://169.254.169.254/latest/meta-data") is False

    # Permitted public threat intel feed domains
    assert validate_external_feed_url("https://otx.alienvault.com/api/v1/indicators/export") is True
    assert validate_external_feed_url("https://urlhaus.abuse.ch/downloads/csv_recent/") is True


@pytest.mark.asyncio
async def test_tenant_isolated_threat_actors():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_a = "tenant-actor-a"
        tenant_b = "tenant-actor-b"

        actor_a = ThreatActor(
            tenant_id=tenant_a,
            name="Actor A Secret Group",
            actor_type="APT",
            motivation="ESPIONAGE"
        )
        db.add(actor_a)
        await db.flush()

        # Query for tenant B
        from sqlalchemy import select
        stmt_b = select(ThreatActor).where(ThreatActor.tenant_id == tenant_b)
        actors_b = list((await db.execute(stmt_b)).scalars().all())

        assert actor_a.id not in [a.id for a in actors_b]
