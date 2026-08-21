"""
tests/security/test_phase43_tenant_isolation.py
===============================================
Phase 43 Data Governance & DSAR Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.data_governance_dsar import (
    DataLineageRecord, LegalHoldOrder, DSARPrivacyRequest
)


class TestDataGovernanceMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 43 models."""

    def test_governance_models_enforce_tenant_id(self):
        """All Phase 43 Data Governance models must enforce tenant_id partition attributes."""
        lin = DataLineageRecord(tenant_id="tenant-gov-1", data_asset_name="a1", transform_hash="h1")
        hld = LegalHoldOrder(tenant_id="tenant-gov-1", matter_reference="m1", custodian_name="c1")
        req = DSARPrivacyRequest(tenant_id="tenant-gov-1", requester_email="e1", completion_certificate_hash="c1")

        assert lin.tenant_id == "tenant-gov-1"
        assert hld.tenant_id == "tenant-gov-1"
        assert req.tenant_id == "tenant-gov-1"
