"""
tests/unit/test_hunting_rules.py
================================
Phase 3.8 Unit Tests: Modular Threat Hunting Detection Rules (HUNT-001 to HUNT-010).
"""

import pytest
from backend.app.hunting import hunt_rule_registry


@pytest.mark.unit
def test_hunt_001_repeated_auth_failure_to_success():
    """Verify HUNT-001 detects authentication failure burst followed by success."""
    events = [
        {"username": "victim_user", "auth_failures": 3, "auth_success": False},
        {"username": "victim_user", "auth_failures": 2, "auth_success": False},
        {"username": "victim_user", "auth_failures": 0, "auth_success": True}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-001", events)
    assert len(findings) == 1
    assert findings[0]["hunt_id"] == "HUNT-001"
    assert findings[0]["entity"] == "victim_user"
    assert findings[0]["mitre_technique"] == "T1110.001"


@pytest.mark.unit
def test_hunt_002_new_source_privileged_access():
    """Verify HUNT-002 detects new source IP granting admin login."""
    events = [
        {"user": "admin_ops", "source_ip": "198.51.100.22", "is_privileged": True, "is_new_source": True}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-002", events)
    assert len(findings) == 1
    assert findings[0]["hunt_id"] == "HUNT-002"
    assert findings[0]["severity"] == "CRITICAL"


@pytest.mark.unit
def test_hunt_003_unusual_lateral_movement():
    """Verify HUNT-003 detects internal administrative port traversal."""
    events = [
        {"source_ip": "10.0.0.15", "destination_ip": "10.0.0.80", "destination_port": 445, "is_internal": True}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-003", events)
    assert len(findings) == 1
    assert findings[0]["mitre_technique"] == "T1021.002"


@pytest.mark.unit
def test_hunt_004_high_volume_outbound():
    """Verify HUNT-004 identifies high-volume outbound data flow."""
    events = [
        {"destination_ip": "203.0.113.88", "bytes_transferred": 15000000, "flow_duration": 4000000}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-004", events)
    assert len(findings) == 1
    assert findings[0]["hunt_id"] == "HUNT-004"


@pytest.mark.unit
def test_hunt_005_ioc_auth_combination():
    """Verify HUNT-005 identifies threat indicator interacting with auth."""
    events = [
        {"source_ip": "185.220.101.5", "ioc_matched": True, "attack_type": "AUTH_ATTEMPT", "username": "finance_admin"}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-005", events)
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"


@pytest.mark.unit
def test_hunt_006_multi_asset_account_access():
    """Verify HUNT-006 identifies single account touching > 3 internal hosts."""
    events = [
        {"username": "compromised_user", "destination_ip": "10.0.0.11"},
        {"username": "compromised_user", "destination_ip": "10.0.0.12"},
        {"username": "compromised_user", "destination_ip": "10.0.0.13"}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-006", events)
    assert len(findings) == 1
    assert findings[0]["evidence_count"] == 3


@pytest.mark.unit
def test_hunt_007_rare_destination_port():
    """Verify HUNT-007 detects non-standard C2 port egress."""
    events = [
        {"destination_ip": "198.51.100.4", "destination_port": 4444}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-007", events)
    assert len(findings) == 1


@pytest.mark.unit
def test_hunt_008_high_velocity_burst():
    """Verify HUNT-008 detects packet velocity spikes."""
    events = [
        {"source_ip": "192.168.1.99", "packet_rate": 2500.0, "attack_type": "DDoS"}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-008", events)
    assert len(findings) == 1


@pytest.mark.unit
def test_hunt_009_suspicious_admin_activity():
    """Verify HUNT-009 detects privilege escalation events."""
    events = [
        {"username": "soc_analyst", "is_privilege_escalation": True}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-009", events)
    assert len(findings) == 1


@pytest.mark.unit
def test_hunt_010_multi_stage_attack_sequence():
    """Verify HUNT-010 correlates full multi-phase attack progression."""
    events = [
        {"attack_type": "PortScan"},
        {"attack_type": "Brute Force"},
        {"attack_type": "Lateral Movement", "destination_port": 445},
        {"attack_type": "Exfiltration", "bytes_transferred": 5000000}
    ]
    findings = hunt_rule_registry.run_hunt("HUNT-010", events)
    assert len(findings) == 1
    assert findings[0]["confidence"] == 0.99
