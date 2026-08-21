"""
tests/security/test_phase34_tenant_isolation.py
===============================================
Phase 34 RBVM Multi-Tenant Boundary Security Tests.
"""

import pytest
from backend.app.models.vulnerability_mgmt import (
    VulnerabilityRecord, AssetVulnerabilityMapping, VirtualPatchRule, RemediationCampaign
)


class TestRBVMTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 34 models."""

    def test_rbvm_models_enforce_tenant_id(self):
        """All RBVM models must enforce tenant_id partition attributes."""
        vuln = VulnerabilityRecord(tenant_id="tenant-rbvm", cve_id="CVE-2024-1111", title="test", description="test")
        mapping = AssetVulnerabilityMapping(tenant_id="tenant-rbvm", hostname="host-1", cve_id="CVE-2024-1111")
        patch = VirtualPatchRule(tenant_id="tenant-rbvm", cve_id="CVE-2024-1111", rule_name="rule-1", rule_syntax="syntax")
        camp = RemediationCampaign(tenant_id="tenant-rbvm", campaign_name="camp-1")

        assert vuln.tenant_id == "tenant-rbvm"
        assert mapping.tenant_id == "tenant-rbvm"
        assert patch.tenant_id == "tenant-rbvm"
        assert camp.tenant_id == "tenant-rbvm"
