"""
tests/unit/test_threat_intel_cache.py
======================================
Phase 3.4 Unit Tests: Fast In-Memory IOC Cache Engine.
Verifies O(1) matching, CIDR range evaluation, domain/hash lookup, stats, and invalidation.
"""

import pytest
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.services.threat_intel_service import FastIOCCache


@pytest.mark.unit
def test_fast_ioc_cache_warmup_and_size():
    """Verify warming up cache with indicators correctly populates memory stores."""
    cache = FastIOCCache()
    assert cache.is_warmed is False
    assert cache.size == 0

    indicators = [
        ThreatIndicator(
            id="ioc-1",
            raw_value="192.168.1.50",
            normalized_value="192.168.1.50",
            ioc_type="ipv4",
            threat_type="c2",
            severity="HIGH",
            confidence=0.90,
            is_active=True,
            lifecycle_status="ACTIVE"
        ),
        ThreatIndicator(
            id="ioc-2",
            raw_value="10.10.0.0/16",
            normalized_value="10.10.0.0/16",
            ioc_type="ipv4",
            threat_type="scanner",
            severity="MEDIUM",
            confidence=0.85,
            is_active=True,
            lifecycle_status="ACTIVE"
        ),
        ThreatIndicator(
            id="ioc-3",
            raw_value="evil-domain.com",
            normalized_value="evil-domain.com",
            ioc_type="domain",
            threat_type="phishing",
            severity="CRITICAL",
            confidence=0.99,
            is_active=False,  # Inactive -> should be excluded
            lifecycle_status="EXPIRED"
        )
    ]

    loaded = cache.warm_up(indicators)
    assert loaded == 2
    assert cache.is_warmed is True
    assert cache.size == 2


@pytest.mark.unit
def test_fast_ioc_cache_exact_and_cidr_ip_matching():
    """Verify exact IP lookup and CIDR subnet containment evaluation."""
    cache = FastIOCCache()
    indicators = [
        ThreatIndicator(
            id="ioc-exact",
            raw_value="45.154.255.89",
            normalized_value="45.154.255.89",
            ioc_type="ipv4",
            threat_type="c2",
            severity="CRITICAL",
            confidence=0.98,
            is_active=True,
            lifecycle_status="ACTIVE"
        ),
        ThreatIndicator(
            id="ioc-cidr",
            raw_value="172.16.0.0/12",
            normalized_value="172.16.0.0/12",
            ioc_type="ipv4",
            threat_type="botnet",
            severity="HIGH",
            confidence=0.88,
            is_active=True,
            lifecycle_status="ACTIVE"
        )
    ]
    cache.warm_up(indicators)

    # Exact match
    match = cache.match_ip("45.154.255.89")
    assert match is not None
    assert match["indicator_id"] == "ioc-exact"
    assert match["severity"] == "CRITICAL"

    # CIDR subnet match (172.16.50.12 falls in 172.16.0.0/12)
    match_cidr = cache.match_ip("172.16.50.12")
    assert match_cidr is not None
    assert match_cidr["indicator_id"] == "ioc-cidr"

    # Non-match
    assert cache.match_ip("8.8.8.8") is None


@pytest.mark.unit
def test_fast_ioc_cache_domain_and_hash_matching():
    """Verify domain, URL, and cryptographic hash matching."""
    cache = FastIOCCache()
    indicators = [
        ThreatIndicator(
            id="ioc-dom",
            raw_value="c2.apt29-malware.org",
            normalized_value="c2.apt29-malware.org",
            ioc_type="domain",
            threat_type="c2",
            severity="CRITICAL",
            confidence=0.95,
            is_active=True,
            lifecycle_status="ACTIVE"
        ),
        ThreatIndicator(
            id="ioc-hash",
            raw_value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            normalized_value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            ioc_type="sha256",
            threat_type="ransomware",
            severity="CRITICAL",
            confidence=1.0,
            is_active=True,
            lifecycle_status="ACTIVE"
        )
    ]
    cache.warm_up(indicators)

    # Domain match (case-insensitive)
    match_dom = cache.match_domain_or_hash("C2.APT29-MALWARE.ORG")
    assert match_dom is not None
    assert match_dom["indicator_id"] == "ioc-dom"

    # Hash match
    match_hash = cache.match_domain_or_hash("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    assert match_hash is not None
    assert match_hash["indicator_id"] == "ioc-hash"

    # Non-match
    assert cache.match_domain_or_hash("google.com") is None


@pytest.mark.unit
def test_fast_ioc_cache_multi_check_and_stats():
    """Verify fast_check evaluates multi-entity tuples and tracks lookup stats."""
    cache = FastIOCCache()
    indicators = [
        ThreatIndicator(
            id="ioc-src",
            raw_value="192.168.1.10",
            normalized_value="192.168.1.10",
            ioc_type="ipv4",
            threat_type="scanner",
            severity="LOW",
            confidence=0.70,
            is_active=True,
            lifecycle_status="ACTIVE"
        )
    ]
    cache.warm_up(indicators)

    matches = cache.fast_check(source_ip="192.168.1.10", destination_ip="10.0.0.1", domain=None)
    assert len(matches) == 1
    assert matches[0]["indicator_id"] == "ioc-src"

    stats = cache.get_stats()
    assert stats["is_warmed"] is True
    assert stats["cached_indicators"] == 1
    assert stats["total_lookups"] >= 2
    assert stats["total_hits"] >= 1
    assert stats["hit_ratio"] > 0.0

    # Invalidate cache
    cache.invalidate()
    assert cache.is_warmed is False
