"""
tests/unit/test_phase36_microsegmentation_posture.py
====================================================
Phase 36 ZTNA Session & Posture Unit Tests.
"""

import pytest
from backend.app.models.microsegmentation import ZTNAAccessSession


class TestMicrosegmentationPosture:
    """Unit tests for ZTNAAccessSession model."""

    def test_ztna_access_session_model(self):
        """ZTNAAccessSession must track user identity, device ID, overlay IP, trust score, and status."""
        session = ZTNAAccessSession(
            tenant_id="tenant-ztna",
            user_email="analyst@corp.internal",
            device_id="DEV-MAC-9912",
            connector_node_name="gw-us-east",
            client_overlay_ip="100.64.1.20",
            target_application="vault.internal:8200",
            current_trust_score=95,
            session_status="ACTIVE_TUNNEL"
        )
        assert session.user_email == "analyst@corp.internal"
        assert session.current_trust_score == 95
        assert session.session_status == "ACTIVE_TUNNEL"
