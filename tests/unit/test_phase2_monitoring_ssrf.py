"""
tests/unit/test_phase2_monitoring_ssrf.py
=========================================
Unit Tests for Continuous Monitoring Enterprise SSRF Protection,
IPv4-Mapped IPv6 Blocking, Multi-IP Resolution, and Deterministic Alert Confidence.
"""

import pytest
import ipaddress
from backend.app.services.monitoring_service import validate_target_url_safe, is_ip_prohibited


def test_ssrf_rejects_loopback_ipv4():
    """Verify loopback IPv4 (127.0.0.1) is blocked by SSRF policy."""
    is_safe, reason, _, _ = validate_target_url_safe("http://127.0.0.1/admin", allow_private=False)
    assert is_safe is False
    assert "SSRF Block" in reason or "loopback" in reason


def test_ssrf_rejects_localhost_hostname():
    """Verify localhost hostname is blocked by SSRF policy."""
    is_safe, reason, _, _ = validate_target_url_safe("http://localhost:8000/api", allow_private=False)
    assert is_safe is False
    assert "rejected by SSRF security policy" in reason


def test_ssrf_rejects_private_class_a():
    """Verify 10.0.0.0/8 private network is blocked."""
    is_safe, reason, _, _ = validate_target_url_safe("http://10.10.10.50/metrics", allow_private=False)
    assert is_safe is False
    assert "SSRF Block" in reason or "private" in reason


def test_ssrf_rejects_private_class_b():
    """Verify 172.16.0.0/12 private network is blocked."""
    is_safe, reason, _, _ = validate_target_url_safe("http://172.20.1.1/status", allow_private=False)
    assert is_safe is False
    assert "SSRF Block" in reason or "private" in reason


def test_ssrf_rejects_private_class_c():
    """Verify 192.168.0.0/16 private network is blocked."""
    is_safe, reason, _, _ = validate_target_url_safe("http://192.168.1.254/router", allow_private=False)
    assert is_safe is False
    assert "SSRF Block" in reason or "private" in reason


def test_ssrf_rejects_cloud_metadata_ip():
    """Verify AWS/GCP/Azure link-local cloud metadata (169.254.169.254) is blocked."""
    is_safe, reason, _, _ = validate_target_url_safe("http://169.254.169.254/latest/meta-data/", allow_private=False)
    assert is_safe is False
    assert "SSRF Block" in reason or "rejected by SSRF" in reason


def test_ssrf_rejects_ipv4_mapped_ipv6_loopback_and_private():
    """Verify IPv4-mapped IPv6 representations of private/loopback addresses are blocked."""
    ip_mapped_loopback = ipaddress.ip_address("::ffff:127.0.0.1")
    prohibited, reason = is_ip_prohibited(ip_mapped_loopback)
    assert prohibited is True
    assert "SSRF Block" in reason or "loopback" in reason

    ip_mapped_private = ipaddress.ip_address("::ffff:192.168.1.1")
    prohibited_priv, reason_priv = is_ip_prohibited(ip_mapped_private)
    assert prohibited_priv is True
    assert "SSRF Block" in reason_priv or "private" in reason_priv


def test_ssrf_rejects_gcp_metadata_hostname():
    """Verify metadata.google.internal is blocked."""
    is_safe, reason, _, _ = validate_target_url_safe("http://metadata.google.internal/computeMetadata/v1/", allow_private=False)
    assert is_safe is False
    assert "rejected by SSRF security policy" in reason


def test_ssrf_rejects_disallowed_protocols():
    """Verify non-HTTP(S) schemes such as file:// or ftp:// are rejected."""
    is_safe, reason, _, _ = validate_target_url_safe("file:///etc/passwd", allow_private=False)
    assert is_safe is False
    assert "Only HTTP and HTTPS are permitted" in reason

    is_safe_ftp, reason_ftp, _, _ = validate_target_url_safe("ftp://ftp.example.com/data", allow_private=False)
    assert is_safe_ftp is False


def test_ssrf_rejects_empty_or_malformed_url():
    """Verify empty or missing hostname URLs are rejected."""
    is_safe, reason, _, _ = validate_target_url_safe("", allow_private=False)
    assert is_safe is False

    is_safe_no_host, reason_no_host, _, _ = validate_target_url_safe("http://", allow_private=False)
    assert is_safe_no_host is False


def test_ssrf_allows_valid_public_url():
    """Verify legitimate public internet domain passes SSRF validation."""
    is_safe, reason, resolved_ip, all_ips = validate_target_url_safe("https://cloudflare.com", allow_private=False)
    assert is_safe is True
    assert resolved_ip is not None
    assert len(all_ips) > 0


@pytest.mark.asyncio
async def test_monitoring_outage_escalation_uses_deterministic_confidence():
    """Verify monitoring outage alerts explicitly tag confidence source and do NOT fabricate ML probabilities."""
    from backend.app.services.monitoring_service import MonitoringService
    from backend.app.models.monitoring import MonitoringCheck
    from backend.app.models.protected_asset import ProtectedAsset
    from backend.app.models.alert import Alert
    from backend.app.database import AsyncSessionFactory
    from sqlalchemy import select

    async with AsyncSessionFactory() as db:
        asset = ProtectedAsset(
            name="Monitoring Confidence Test Asset",
            hostname="mon-conf.corp",
            ip_address="198.51.100.33",
            asset_type="api",
            criticality="high"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        check = MonitoringCheck(
            asset_id=asset.id,
            monitor_type="HTTP",
            target_url="https://api.sentinelai.io/health",
            expected_status_code=200,
            consecutive_failures=3,
            health_state="DOWN"
        )
        db.add(check)
        await db.commit()
        await db.refresh(check)

        # Trigger escalation
        await MonitoringService._escalate_persistent_outage(check, db)
        await db.commit()

        # Query created alert
        res = await db.execute(select(Alert).where(Alert.asset_id == asset.id).order_by(Alert.created_at.desc()).limit(1))
        alert = res.scalar_one_or_none()
        assert alert is not None
        assert alert.explanation.get("confidence_source") == "DETERMINISTIC_HEALTH_PROBE"
        assert alert.explanation.get("is_ml_generated") is False
