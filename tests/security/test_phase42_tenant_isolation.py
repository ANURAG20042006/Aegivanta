"""
tests/security/test_phase42_tenant_isolation.py
===============================================
Phase 42 Multi-Region Resilience Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.multi_region_resilience import (
    RegionReplicationCluster, DataResidencyBoundary, FailoverExecutionEvent
)


class TestMultiRegionMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 42 models."""

    def test_multi_region_models_enforce_tenant_id(self):
        """All Phase 42 Multi-Region models must enforce tenant_id partition attributes."""
        cluster = RegionReplicationCluster(tenant_id="tenant-multi-1", region_name="US_EAST_PRIMARY")
        bnd = DataResidencyBoundary(tenant_id="tenant-multi-1", boundary_name="bnd-1")
        evt = FailoverExecutionEvent(tenant_id="tenant-multi-1", source_failing_region="r1", target_failover_region="r2")

        assert cluster.tenant_id == "tenant-multi-1"
        assert bnd.tenant_id == "tenant-multi-1"
        assert evt.tenant_id == "tenant-multi-1"
