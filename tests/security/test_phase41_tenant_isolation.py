"""
tests/security/test_phase41_tenant_isolation.py
===============================================
Phase 41 Edge Security Fabric Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.edge_security_fabric import (
    GlobalEdgePoPNode, EdgeInspectionPolicy, RegionalIngestionRoute
)


class TestEdgeMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 41 models."""

    def test_edge_models_enforce_tenant_id(self):
        """All Phase 41 Edge Security Fabric models must enforce tenant_id partition attributes."""
        pop = GlobalEdgePoPNode(tenant_id="tenant-edge-1", region_code="US_EAST_VA", pop_location_name="Ashburn")
        pol = EdgeInspectionPolicy(tenant_id="tenant-edge-1", policy_name="p1")
        rte = RegionalIngestionRoute(tenant_id="tenant-edge-1", source_region="r1", target_core_cluster="c1")

        assert pop.tenant_id == "tenant-edge-1"
        assert pol.tenant_id == "tenant-edge-1"
        assert rte.tenant_id == "tenant-edge-1"
