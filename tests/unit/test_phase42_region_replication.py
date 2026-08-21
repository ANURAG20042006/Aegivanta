"""
tests/unit/test_phase42_region_replication.py
=============================================
Phase 42 Region Replication Cluster Unit Tests.
"""

import pytest
from backend.app.models.multi_region_resilience import RegionReplicationCluster


class TestRegionReplication:
    """Unit tests for RegionReplicationCluster model."""

    def test_replication_cluster_model_creation(self):
        """RegionReplicationCluster must store region, role, lag, RPO, and RTO."""
        cluster = RegionReplicationCluster(
            tenant_id="tenant-multi",
            region_name="US_EAST_PRIMARY",
            cluster_role="ACTIVE_PRIMARY",
            health_status="ONLINE",
            replication_lag_ms=1.45,
            rpo_seconds=0.0,
            rto_seconds=1.5
        )
        assert cluster.region_name == "US_EAST_PRIMARY"
        assert cluster.cluster_role == "ACTIVE_PRIMARY"
        assert cluster.replication_lag_ms == 1.45
        assert cluster.rpo_seconds == 0.0
