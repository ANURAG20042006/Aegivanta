"""
tests/unit/test_phase36_lateral_movement.py
===========================================
Phase 36 Lateral Movement Interception Unit Tests.
"""

import pytest
from backend.app.models.microsegmentation import LateralMovementBlockedAlert


class TestLateralMovement:
    """Unit tests for LateralMovementBlockedAlert model."""

    def test_lateral_movement_alert_model(self):
        """LateralMovementBlockedAlert must track source and target workloads, segments, and action."""
        alert = LateralMovementBlockedAlert(
            tenant_id="tenant-ztna",
            source_workload="compromised-pod-01",
            source_segment="DEV_ENV",
            target_workload="db-master",
            target_segment="PROD_DB",
            attempted_port_protocol="TCP/5432",
            interception_action="BLOCKED_AND_ISOLATED",
            threat_classification="UNAUTHORIZED_LATERAL_PIVOT"
        )
        assert alert.source_workload == "compromised-pod-01"
        assert alert.interception_action == "BLOCKED_AND_ISOLATED"
        assert alert.threat_classification == "UNAUTHORIZED_LATERAL_PIVOT"
