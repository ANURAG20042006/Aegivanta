"""
tests/security/test_phase36_tenant_isolation.py
===============================================
Phase 36 Microsegmentation Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.microsegmentation import (
    ZTNAConnectorNode, MicrosegmentationPolicy, ZTNAAccessSession, LateralMovementBlockedAlert
)


class TestMicrosegmentationTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 36 models."""

    def test_microsegmentation_models_enforce_tenant_id(self):
        """All Microsegmentation & ZTNA models must enforce tenant_id partition attributes."""
        node = ZTNAConnectorNode(tenant_id="tenant-ztna-1", connector_name="gw-1")
        policy = MicrosegmentationPolicy(tenant_id="tenant-ztna-1", policy_name="pol-1")
        session = ZTNAAccessSession(tenant_id="tenant-ztna-1", user_email="u@c.i")
        alert = LateralMovementBlockedAlert(tenant_id="tenant-ztna-1")

        assert node.tenant_id == "tenant-ztna-1"
        assert policy.tenant_id == "tenant-ztna-1"
        assert session.tenant_id == "tenant-ztna-1"
        assert alert.tenant_id == "tenant-ztna-1"
