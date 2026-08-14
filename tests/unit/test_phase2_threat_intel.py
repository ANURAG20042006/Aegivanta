"""
tests/unit/test_phase2_threat_intel.py
======================================
Unit Tests for Threat Intelligence Normalization, Providers, and Ingestion.
"""

import pytest
from backend.app.services.threat_intel_service import normalize_ioc, StaticListProvider, GenericJsonProvider
from backend.app.models.threat_intel import ThreatFeed


def test_ioc_normalization_ipv4():
    """Test IPv4 address normalization."""
    is_valid, norm_val, det_type = normalize_ioc(" 198.51.100.22  ", "ipv4")
    assert is_valid is True
    assert norm_val == "198.51.100.22"
    assert det_type == "ipv4"


def test_ioc_normalization_ipv6():
    """Test IPv6 address normalization."""
    is_valid, norm_val, det_type = normalize_ioc("2001:0db8:85a3:0000:0000:8a2e:0370:7334", "ipv6")
    assert is_valid is True
    assert det_type == "ipv6"
    assert "2001:db8:85a3::8a2e:370:7334" in norm_val or "2001:0db8" in norm_val


def test_ioc_normalization_domain():
    """Test domain name normalization with protocols, ports, and casing."""
    is_valid, norm_val, det_type = normalize_ioc("https://C2-Server.Malicious.IO:8443/payload", "domain")
    assert is_valid is True
    assert norm_val == "c2-server.malicious.io"
    assert det_type == "domain"


def test_ioc_normalization_url():
    """Test URL normalization."""
    is_valid, norm_val, det_type = normalize_ioc("https://EVIL-DOMAIN.COM/path/to/drop?key=123", "url")
    assert is_valid is True
    assert norm_val.startswith("https://evil-domain.com/path/to/drop")
    assert det_type == "url"


def test_ioc_normalization_sha256_hash():
    """Test SHA-256 hash normalization."""
    valid_hash = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
    is_valid, norm_val, det_type = normalize_ioc(valid_hash, "sha256")
    assert is_valid is True
    assert norm_val == valid_hash.lower()
    assert det_type == "sha256"


def test_ioc_normalization_invalid_rejected():
    """Test invalid or malformed IOC strings are rejected."""
    is_valid, norm_val, _ = normalize_ioc("not_an_ip_or_domain", "ipv4")
    assert is_valid is False

    is_valid_empty, _, _ = normalize_ioc("", "domain")
    assert is_valid_empty is False


@pytest.mark.asyncio
async def test_static_list_provider_parsing():
    """Test StaticListProvider parsing JSON serialized records."""
    raw_json = '[{"value": "203.0.113.5", "type": "ipv4", "threat_type": "botnet", "severity": "HIGH", "confidence": 0.95}]'
    feed = ThreatFeed(feed_name="Test_Static_Feed", provider_type="static_list", feed_url=raw_json)
    
    provider = StaticListProvider()
    records = await provider.fetch_and_parse(feed)
    assert len(records) == 1
    assert records[0]["value"] == "203.0.113.5"
    assert records[0]["threat_type"] == "botnet"
