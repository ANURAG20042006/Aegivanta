"""
tests/unit/test_phase41_edge_inspection.py
==========================================
Phase 41 Edge Inspection Policy Unit Tests.
"""

import pytest
from backend.app.models.edge_security_fabric import EdgeInspectionPolicy


class TestEdgeInspection:
    """Unit tests for EdgeInspectionPolicy model."""

    def test_edge_policy_model_creation(self):
        """EdgeInspectionPolicy must store name, mode, and rate limit."""
        pol = EdgeInspectionPolicy(
            tenant_id="tenant-edge",
            policy_name="L7 DDoS Scrubbing",
            inspection_mode="SCRUB_DDOS",
            edge_rate_limit_rps=100000,
            geo_fence_action="BLOCK",
            enabled=True
        )
        assert pol.policy_name == "L7 DDoS Scrubbing"
        assert pol.inspection_mode == "SCRUB_DDOS"
        assert pol.edge_rate_limit_rps == 100000
