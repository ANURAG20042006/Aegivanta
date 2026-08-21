"""
tests/unit/test_phase31_dangling_dns.py
=======================================
Phase 31 Dangling DNS & Subdomain Takeover Unit Tests.
"""

import pytest
from backend.app.models.attack_surface import DanglingDNSRisk


class TestDanglingDNS:
    """Unit tests for dangling DNS record detection models."""

    def test_dangling_dns_model_initialization(self):
        """DanglingDNSRisk must store target CNAME, service type, and takeover risk score."""
        dd = DanglingDNSRisk(
            tenant_id="tenant-123",
            subdomain="docs-staging.aegivanta.io",
            cname_target="aegivanta-docs.s3-website-us-east-1.amazonaws.com",
            target_service="AWS_S3",
            takeover_risk_score=95.0,
            is_takeover_verified=True,
            status="VULNERABLE"
        )
        assert dd.subdomain == "docs-staging.aegivanta.io"
        assert dd.target_service == "AWS_S3"
        assert dd.takeover_risk_score == 95.0
        assert dd.status == "VULNERABLE"
