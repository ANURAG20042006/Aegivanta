"""
tests/unit/test_phase41_regional_routing.py
===========================================
Phase 41 Regional Ingestion WAN Routing Unit Tests.
"""

import pytest
from backend.app.models.edge_security_fabric import RegionalIngestionRoute


class TestRegionalRouting:
    """Unit tests for RegionalIngestionRoute model."""

    def test_regional_route_model_creation(self):
        """RegionalIngestionRoute must store source region, target cluster, and protocol."""
        rte = RegionalIngestionRoute(
            tenant_id="tenant-edge",
            source_region="EU_CENTRAL_FRA",
            target_core_cluster="Core-Cluster-EU",
            routing_protocol="WIREGUARD_MTLS",
            replication_lag_ms=1.5,
            is_primary=True
        )
        assert rte.source_region == "EU_CENTRAL_FRA"
        assert rte.target_core_cluster == "Core-Cluster-EU"
        assert rte.replication_lag_ms == 1.5
