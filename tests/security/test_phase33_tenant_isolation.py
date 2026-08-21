"""
tests/security/test_phase33_tenant_isolation.py
===============================================
Phase 33 Deception Multi-Tenant Boundary Security Tests.
"""

import pytest
from backend.app.models.deception import (
    HoneypotNode, CanaryToken, DeceptionInteractionEvent, EndpointLureDeployment
)


class TestDeceptionTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 33 models."""

    def test_deception_models_enforce_tenant_id(self):
        """All deception models must enforce tenant_id partition attributes."""
        pot = HoneypotNode(tenant_id="tenant-dec", node_name="pot-1", internal_ip="10.0.0.1")
        canary = CanaryToken(tenant_id="tenant-dec", token_name="can-1", trigger_url_or_domain="url")
        intx = DeceptionInteractionEvent(tenant_id="tenant-dec", source_ip="1.1.1.1", target_decoy_name="pot-1", captured_payload_or_command="cmd")
        lure = EndpointLureDeployment(tenant_id="tenant-dec", endpoint_hostname="host-1")

        assert pot.tenant_id == "tenant-dec"
        assert canary.tenant_id == "tenant-dec"
        assert intx.tenant_id == "tenant-dec"
        assert lure.tenant_id == "tenant-dec"
