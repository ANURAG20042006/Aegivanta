import pytest
from backend.app.models.incident import (
    Incident,
    is_valid_state_transition,
    ALLOWED_STATE_TRANSITIONS,
    VALID_INCIDENT_STATUSES
)


def test_incident_state_machine_valid_transitions():
    """Requirement 1 Proof: Valid state machine transitions are accepted."""
    assert is_valid_state_transition("DETECTED", "TRIAGED") is True
    assert is_valid_state_transition("TRIAGED", "INVESTIGATING") is True
    assert is_valid_state_transition("INVESTIGATING", "CONTAINED") is True
    assert is_valid_state_transition("CONTAINED", "RESOLVED") is True
    assert is_valid_state_transition("RESOLVED", "CLOSED") is True
    # Same status self-transition is valid
    assert is_valid_state_transition("TRIAGED", "TRIAGED") is True


def test_incident_state_machine_invalid_transitions():
    """Requirement 1 Proof: Invalid state jumps are rejected."""
    # DETECTED directly to CLOSED without triaging/investigating
    assert is_valid_state_transition("DETECTED", "CLOSED") is False
    # CLOSED to DETECTED (no backward transitions from closed)
    assert is_valid_state_transition("CLOSED", "DETECTED") is False
    # RESOLVED to TRIAGED
    assert is_valid_state_transition("RESOLVED", "TRIAGED") is False


def test_incident_model_fields():
    """Requirement 2 Proof: Incident model stores required lifecycle attributes."""
    incident = Incident(
        alert_id="ALT-12345678",
        status="DETECTED",
        source_ip="192.168.1.100",
        destination_ip="10.0.0.1",
        source_port=5000,
        destination_port=80,
        protocol="TCP",
        packet_length=1200,
        attack_type="DDoS",
        confidence_score=0.9910,
        is_malicious=True,
        severity="Critical",
        model_name="XGBoost",
        model_version="xgboost-v1.0",
        analyst="soc_analyst_1",
        notes="High volume SYN flood detected on port 80",
        remediation_action="[SIMULATION MODE] Action: BLOCK_IP on IP 192.168.1.100"
    )

    assert incident.alert_id == "ALT-12345678"
    assert incident.status in VALID_INCIDENT_STATUSES
    assert incident.attack_type == "DDoS"
    assert incident.model_version == "xgboost-v1.0"
    assert "BLOCK_IP" in incident.remediation_action
