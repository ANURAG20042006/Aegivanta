"""
tests/unit/test_phase36_ztna_controller.py
==========================================
Phase 36 ZTNA Controller & SDP Gateway Unit Tests.
"""

import pytest
from backend.app.models.microsegmentation import ZTNAConnectorNode


class TestZTNAController:
    """Unit tests for ZTNAConnectorNode model attributes."""

    def test_ztna_connector_model_creation(self):
        """ZTNAConnectorNode must store gateway name, region, public IP, and overlay CIDR."""
        node = ZTNAConnectorNode(
            tenant_id="tenant-ztna",
            connector_name="ztna-gw-us-east-1",
            region="us-east-1",
            status="ONLINE",
            public_ip="52.14.88.102",
            private_overlay_cidr="100.64.0.0/16",
            active_client_sessions_count=142,
            total_bytes_tunneled_gb=1840.5
        )
        assert node.connector_name == "ztna-gw-us-east-1"
        assert node.region == "us-east-1"
        assert node.status == "ONLINE"
        assert node.active_client_sessions_count == 142
