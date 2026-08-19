"""
tests/unit/test_threat_intel_lifecycle.py
=========================================
Phase 3.4 Unit Tests: Threat Intelligence IOC Lifecycle & Pruning Engine.
Verifies normalization, TTL aging, confidence pruning, hard-purge, and lifecycle metrics.
"""

import pytest
import datetime
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

from backend.app.models.threat_intel import ThreatIndicator, ThreatFeed
from backend.app.services.threat_intel_service import ThreatIntelService, normalize_ioc


@pytest.mark.unit
def test_normalize_ioc_comprehensive():
    """Verify IOC normalization for IPv4, IPv6, domain, URL, and hashes."""
    # IPv4
    valid, norm, dtype = normalize_ioc(" 192.168.1.100 ", "ipv4")
    assert valid is True
    assert norm == "192.168.1.100"
    assert dtype == "ipv4"

    # IPv6
    valid, norm, dtype = normalize_ioc("2001:0db8:85a3:0000:0000:8a2e:0370:7334", "ipv6")
    assert valid is True
    assert dtype == "ipv6"

    # Domain
    valid, norm, dtype = normalize_ioc("https://evil-c2-domain.com:8080/path", "domain")
    assert valid is True
    assert norm == "evil-c2-domain.com"
    assert dtype == "domain"

    # URL
    valid, norm, dtype = normalize_ioc("HTTP://MALICIOUS.ORG/PAYLOAD.EXE?ID=1", "url")
    assert valid is True
    assert norm == "http://malicious.org/PAYLOAD.EXE?ID=1"
    assert dtype == "url"

    # SHA256
    valid, norm, dtype = normalize_ioc("E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855", "sha256")
    assert valid is True
    assert norm == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert dtype == "sha256"

    # Invalid input
    valid, norm, dtype = normalize_ioc("invalid-ip-999.999.999.999", "ipv4")
    assert valid is False


@pytest.mark.unit
def test_threat_indicator_model_attributes():
    """Verify ThreatIndicator model includes lifecycle fields."""
    ind = ThreatIndicator(
        raw_value="1.2.3.4",
        normalized_value="1.2.3.4",
        ioc_type="ipv4",
        threat_type="c2",
        lifecycle_status="ACTIVE",
        is_active=True,
        hit_count=0
    )
    assert ind.lifecycle_status == "ACTIVE"
    assert ind.is_active is True
    assert ind.hit_count == 0


@pytest.mark.asyncio
async def test_prune_expired_iocs_ttl():
    """Verify indicators with expired TTL are transitioned to EXPIRED."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    past_date = now - timedelta(days=5)

    expired_ind = ThreatIndicator(
        id="ioc-1",
        raw_value="10.0.0.99",
        normalized_value="10.0.0.99",
        ioc_type="ipv4",
        expires_at=past_date,
        is_active=True,
        confidence=0.90
    )
    active_ind = ThreatIndicator(
        id="ioc-2",
        raw_value="10.0.0.100",
        normalized_value="10.0.0.100",
        ioc_type="ipv4",
        expires_at=now + timedelta(days=30),
        is_active=True,
        confidence=0.95
    )

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [expired_ind, active_ind]
    mock_db.execute.return_value = mock_res

    res = await ThreatIntelService.prune_expired_iocs(mock_db, max_age_days=90, min_confidence=0.20, purge_deleted=False)

    assert res["total_evaluated"] == 2
    assert res["pruned_count"] == 1
    assert res["active_remaining"] == 1
    assert expired_ind.is_active is False
    assert expired_ind.lifecycle_status == "EXPIRED"
    assert active_ind.is_active is True


@pytest.mark.asyncio
async def test_prune_expired_iocs_stale_age():
    """Verify stale indicators older than max_age_days are ARCHIVED."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    stale_date = now - timedelta(days=120)

    stale_ind = ThreatIndicator(
        id="ioc-stale",
        raw_value="c2.staledomain.org",
        normalized_value="c2.staledomain.org",
        ioc_type="domain",
        last_seen=stale_date,
        is_active=True,
        confidence=0.80
    )

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [stale_ind]
    mock_db.execute.return_value = mock_res

    res = await ThreatIntelService.prune_expired_iocs(mock_db, max_age_days=90, min_confidence=0.20, purge_deleted=False)

    assert res["pruned_count"] == 1
    assert stale_ind.is_active is False
    assert stale_ind.lifecycle_status == "ARCHIVED"


@pytest.mark.asyncio
async def test_prune_expired_iocs_low_confidence_and_purge():
    """Verify low confidence indicators are hard-purged when purge_deleted=True."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    low_conf_ind = ThreatIndicator(
        id="ioc-low-conf",
        raw_value="198.51.100.1",
        normalized_value="198.51.100.1",
        ioc_type="ipv4",
        last_seen=now,
        is_active=True,
        confidence=0.10  # Below min_confidence 0.20
    )

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [low_conf_ind]
    mock_db.execute.return_value = mock_res

    res = await ThreatIntelService.prune_expired_iocs(mock_db, max_age_days=90, min_confidence=0.20, purge_deleted=True)

    assert res["pruned_count"] == 1
    assert res["purged_count"] == 1
    mock_db.delete.assert_called_once_with(low_conf_ind)


@pytest.mark.asyncio
async def test_get_lifecycle_metrics():
    """Verify get_lifecycle_metrics computes accurate distribution counts."""
    mock_db = AsyncMock()

    # Mock count queries
    res_mock = MagicMock()
    res_mock.scalar.side_effect = [150, 200, 30, 20]
    mock_db.execute.return_value = res_mock

    metrics = await ThreatIntelService.get_lifecycle_metrics(mock_db)

    assert metrics["active_indicators"] == 150
    assert metrics["total_indicators"] == 200
    assert metrics["expired_indicators"] == 30
    assert metrics["archived_indicators"] == 20
    assert metrics["healthy_ratio"] == 0.75
