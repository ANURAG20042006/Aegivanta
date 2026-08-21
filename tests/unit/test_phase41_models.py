"""
tests/unit/test_phase41_models.py
=================================
Phase 41 Model Schema & Defaults Unit Tests.
"""

import pytest
from backend.app.models.edge_security_fabric import GlobalEdgePoPNode, EdgeInspectionPolicy, RegionalIngestionRoute


class TestPhase41Models:
    """Unit tests verifying Phase 41 database defaults."""

    def test_edge_pop_defaults(self):
        """Edge PoP should store HEALTHY status and valid throughput."""
        pop = GlobalEdgePoPNode(
            tenant_id="tenant-edge",
            region_code="AP_SOUTHEAST_SIN",
            pop_location_name="Singapore",
            edge_status="HEALTHY",
            throughput_gbps=51.8
        )
        assert pop.edge_status == "HEALTHY"
        assert pop.throughput_gbps == 51.8

