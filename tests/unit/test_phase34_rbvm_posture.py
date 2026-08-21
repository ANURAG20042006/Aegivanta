"""
tests/unit/test_phase34_rbvm_posture.py
=======================================
Phase 34 RBVM Posture Scorecard & Campaign Unit Tests.
"""

import pytest
from backend.app.models.vulnerability_mgmt import RemediationCampaign


class TestRBVMPosture:
    """Unit tests for Remediation Campaign model."""

    def test_remediation_campaign_model(self):
        """RemediationCampaign must store targeted CVEs, completion counts, and status."""
        camp = RemediationCampaign(
            tenant_id="tenant-123",
            campaign_name="Edge Gateway Sprint",
            target_cves=["CVE-2023-4966"],
            owner_team="SecOps",
            total_targeted_assets=10,
            remediated_assets_count=6,
            status="IN_PROGRESS"
        )
        assert camp.campaign_name == "Edge Gateway Sprint"
        assert camp.total_targeted_assets == 10
        assert camp.remediated_assets_count == 6
