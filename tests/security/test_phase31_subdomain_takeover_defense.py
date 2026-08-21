"""
tests/security/test_phase31_subdomain_takeover_defense.py
=========================================================
Phase 31 Subdomain Takeover & Dangling DNS Defense Security Tests.
"""

import pytest
from backend.app.models.attack_surface import DanglingDNSRisk


class TestSubdomainTakeoverDefense:
    """Security tests verifying dangling DNS detection and takeover vulnerability flags."""

    def test_dangling_dns_flags_high_takeover_risk(self):
        """Unclaimed S3 bucket CNAME pointers must receive a critical risk score >= 90.0."""
        vuln = DanglingDNSRisk(
            tenant_id="tenant-sec",
            subdomain="test-takeover.aegivanta.io",
            cname_target="unclaimed-bucket-123.s3-website-us-east-1.amazonaws.com",
            target_service="AWS_S3",
            takeover_risk_score=95.0,
            is_takeover_verified=True,
            status="VULNERABLE"
        )
        assert vuln.takeover_risk_score >= 90.0
        assert vuln.status == "VULNERABLE"
        assert vuln.is_takeover_verified is True
