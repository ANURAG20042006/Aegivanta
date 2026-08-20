import pytest
from datetime import datetime, timezone, timedelta
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.services.threat_intelligence_platform_service import ThreatIntelligencePlatformService


def test_threat_score_calculation_factors():
    now = datetime.now(timezone.utc)
    ind = ThreatIndicator(
        ioc_type="ipv4",
        raw_value="203.0.113.55",
        normalized_value="203.0.113.55",
        threat_type="c2",
        severity="CRITICAL",
        confidence=0.95,
        source="CISA_KNOWN_EXPLOITED",
        last_seen=now
    )

    score_info = ThreatIntelligencePlatformService.calculate_threat_score(
        indicator=ind,
        sightings_count=5,
        has_campaign=True,
        has_actor=True
    )

    assert score_info["score"] >= 80.0
    assert score_info["risk_tier"] == "CRITICAL"
    assert "explanation" in score_info
    assert score_info["factors"]["source_reliability"] == 20.0
    assert score_info["factors"]["campaign_association"] == 10.0


def test_threat_score_decay_on_old_indicators():
    old_time = datetime.now(timezone.utc) - timedelta(days=120)
    ind = ThreatIndicator(
        ioc_type="domain",
        raw_value="evil-c2-domain.com",
        normalized_value="evil-c2-domain.com",
        threat_type="scanner",
        severity="LOW",
        confidence=0.6,
        source="COMMUNITY_FEED",
        last_seen=old_time
    )

    score_info = ThreatIntelligencePlatformService.calculate_threat_score(
        indicator=ind,
        sightings_count=0,
        has_campaign=False,
        has_actor=False
    )

    assert score_info["decay_factor"] < 1.0
    assert score_info["score"] <= 60.0
