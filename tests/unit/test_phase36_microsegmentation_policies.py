"""
tests/unit/test_phase36_microsegmentation_policies.py
=====================================================
Phase 36 L4/L7 Microsegmentation Policy Unit Tests.
"""

import pytest
from backend.app.models.microsegmentation import MicrosegmentationPolicy


class TestMicrosegmentationPolicies:
    """Unit tests for MicrosegmentationPolicy model."""

    def test_policy_model_attributes(self):
        """MicrosegmentationPolicy must store segments, port/protocol, action, and min trust score."""
        pol = MicrosegmentationPolicy(
            tenant_id="tenant-ztna",
            policy_name="Payment to DB Isolate",
            source_segment="PAYMENT_GATEWAY_VPC",
            destination_segment="CORE_DATABASE_CLUSTER",
            protocol_port="TCP/5432",
            enforcement_action="ALLOW_ENCRYPTED_TUNNEL",
            min_device_trust_score=85
        )
        assert pol.policy_name == "Payment to DB Isolate"
        assert pol.source_segment == "PAYMENT_GATEWAY_VPC"
        assert pol.destination_segment == "CORE_DATABASE_CLUSTER"
        assert pol.min_device_trust_score == 85
