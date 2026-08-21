"""
tests/unit/test_phase35_dlp_posture.py
======================================
Phase 35 DLP Posture & Exfiltration Incident Unit Tests.
"""

import pytest
from backend.app.models.dlp_security import DLPIncidentEvent


class TestDLPPosture:
    """Unit tests for DLP Incident Event tracking."""

    def test_dlp_incident_event_model(self):
        """DLPIncidentEvent must track channel, destination, matched policy, and enforcement action."""
        event = DLPIncidentEvent(
            tenant_id="tenant-dlp",
            source_identity="user@corp.internal",
            channel="API_GATEWAY",
            target_destination="api.partner.com",
            matched_policy_name="PCI PAN Guard",
            data_category="PCI_CARD",
            masked_sample_snippet="4111-XXXX-XXXX-1111",
            violations_count=2,
            enforcement_action_taken="BLOCK_TRANSMISSION"
        )
        assert event.source_identity == "user@corp.internal"
        assert event.enforcement_action_taken == "BLOCK_TRANSMISSION"
        assert event.violations_count == 2
