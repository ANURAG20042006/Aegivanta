"""
tests/unit/test_phase33_adversary_engagement.py
===============================================
Phase 33 Adversary Engagement & Interaction Ledger Unit Tests.
"""

import pytest
from backend.app.models.deception import DeceptionInteractionEvent, EndpointLureDeployment


class TestAdversaryEngagement:
    """Unit tests for adversary interaction events and endpoint lure deployments."""

    def test_interaction_event_model(self):
        """DeceptionInteractionEvent must record source IP, payload, and MITRE Engage activity."""
        event = DeceptionInteractionEvent(
            tenant_id="tenant-123",
            source_ip="198.51.100.44",
            attacker_asn="AS14061 DigitalOcean, LLC",
            target_decoy_name="decoy-ssh-bastion-01",
            interaction_type="COMMAND_EXEC",
            captured_payload_or_command="cat /etc/shadow",
            mitre_engage_activity="EAC0018_ELICIT",
            fidelity_confidence=100.0,
            containment_action_taken="HOST_ISOLATED_BY_SOAR"
        )
        assert event.source_ip == "198.51.100.44"
        assert event.fidelity_confidence == 100.0
        assert event.mitre_engage_activity == "EAC0018_ELICIT"

    def test_endpoint_lure_model(self):
        """EndpointLureDeployment must store target honey user and deployment status."""
        lure = EndpointLureDeployment(
            tenant_id="tenant-123",
            endpoint_hostname="WS-FINANCE-04",
            lure_type="SAVED_CREDENTIAL",
            target_honey_user="svc_sql_backup",
            deployment_status="INJECTED_ACTIVE"
        )
        assert lure.endpoint_hostname == "WS-FINANCE-04"
        assert lure.deployment_status == "INJECTED_ACTIVE"
