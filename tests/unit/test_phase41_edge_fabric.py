"""
tests/unit/test_phase41_edge_fabric.py
======================================
Phase 41 Global Edge PoP Unit Tests.
"""

import pytest
from backend.app.models.edge_security_fabric import GlobalEdgePoPNode


class TestEdgeFabric:
    """Unit tests for GlobalEdgePoPNode model."""

    def test_edge_pop_model_creation(self):
        """GlobalEdgePoPNode must store region code, throughput, and latency."""
        pop = GlobalEdgePoPNode(
            tenant_id="tenant-edge",
            region_code="US_EAST_VA",
            pop_location_name="Ashburn, Virginia",
            edge_status="HEALTHY",
            throughput_gbps=84.5,
            active_connections=245000,
            latency_ms=3.8
        )
        assert pop.region_code == "US_EAST_VA"
        assert pop.throughput_gbps == 84.5
        assert pop.latency_ms == 3.8
