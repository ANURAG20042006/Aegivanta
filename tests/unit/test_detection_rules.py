"""
tests/unit/test_detection_rules.py
==================================
Phase 3.6 Unit Tests: Modular Detection Rule Framework.
Verifies all 10 production detection rules (RULE-001 through RULE-010),
rule registry, deterministic evaluations, and MITRE ATT&CK mappings.
"""

import pytest
from backend.app.detection.rules.production_rules import detection_registry


@pytest.mark.unit
def test_all_10_rules_registered():
    """Verify all 10 production rules are registered in the global registry."""
    rules = detection_registry.get_all_rules()
    assert len(rules) == 10
    rule_ids = {r.rule_id for r in rules}
    for i in range(1, 11):
        assert f"RULE-{i:03d}" in rule_ids


@pytest.mark.unit
def test_rule_001_repeated_auth_failures():
    """Verify RULE-001 triggers on high auth failure count or brute-force attack type."""
    r1 = detection_registry.get_rule("RULE-001")
    # Positive case
    match = r1.evaluate({"source_ip": "192.168.1.50", "attack_type": "Brute Force", "auth_failures": 6})
    assert match is not None
    assert match["matched"] is True
    assert "T1110.001" in match["mitre_techniques"]
    assert match["confidence"] >= 0.85

    # Negative case
    benign = r1.evaluate({"source_ip": "192.168.1.50", "attack_type": "BENIGN", "auth_failures": 0})
    assert benign is None


@pytest.mark.unit
def test_rule_002_impossible_auth_pattern():
    """Verify RULE-002 triggers on impossible travel speed."""
    r2 = detection_registry.get_rule("RULE-002")
    match = r2.evaluate({"user_id": "admin_1", "source_ip": "203.0.113.5", "calculated_travel_speed_kmh": 2500.0})
    assert match is not None
    assert match["severity"] == "CRITICAL"
    assert "T1078.004" in match["mitre_techniques"]

    benign = r2.evaluate({"user_id": "admin_1", "calculated_travel_speed_kmh": 45.0})
    assert benign is None


@pytest.mark.unit
def test_rule_003_ioc_matched_telemetry():
    """Verify RULE-003 triggers when threat intel indicators match flow."""
    r3 = detection_registry.get_rule("RULE-003")
    match = r3.evaluate({
        "source_ip": "10.0.0.5",
        "destination_ip": "198.51.100.1",
        "matched_iocs": [{"value": "198.51.100.1", "threat_type": "C2_SERVER", "severity": "CRITICAL", "confidence": 0.95}]
    })
    assert match is not None
    assert match["severity"] == "CRITICAL"
    assert "T1071.001" in match["mitre_techniques"]

    benign = r3.evaluate({"source_ip": "10.0.0.5", "destination_ip": "10.0.0.1", "matched_iocs": []})
    assert benign is None


@pytest.mark.unit
def test_rule_004_suspicious_lateral_movement():
    """Verify RULE-004 triggers on administrative lateral ports."""
    r4 = detection_registry.get_rule("RULE-004")
    match = r4.evaluate({"source_ip": "10.0.0.10", "destination_ip": "10.0.0.20", "destination_port": 445, "is_malicious": True})
    assert match is not None
    assert "T1021.002" in match["mitre_techniques"]

    benign = r4.evaluate({"source_ip": "10.0.0.10", "destination_ip": "10.0.0.20", "destination_port": 80, "is_malicious": False})
    assert benign is None


@pytest.mark.unit
def test_rule_005_high_risk_multi_hop_path():
    """Verify RULE-005 triggers on multi-hop trajectories >= 3 hops."""
    r5 = detection_registry.get_rule("RULE-005")
    match = r5.evaluate({"hop_count": 3, "cumulative_risk_score": 85.0})
    assert match is not None
    assert match["severity"] == "CRITICAL"

    benign = r5.evaluate({"hop_count": 1, "cumulative_risk_score": 20.0})
    assert benign is None


@pytest.mark.unit
def test_rule_006_crown_jewel_exposure():
    """Verify RULE-006 triggers on high Crown Jewel exposure index."""
    r6 = detection_registry.get_rule("RULE-006")
    match = r6.evaluate({"crown_jewel_exposure_index": 75.0, "critical_assets_exposed": 2})
    assert match is not None
    assert "T1087" in match["mitre_techniques"]

    benign = r6.evaluate({"crown_jewel_exposure_index": 10.0, "critical_assets_exposed": 0})
    assert benign is None


@pytest.mark.unit
def test_rule_007_through_010_evaluations():
    """Verify remaining rules 7, 8, 9, 10."""
    r7 = detection_registry.get_rule("RULE-007")
    m7 = r7.evaluate({"attack_type": "Exfiltration", "flow_duration": 4000.0, "total_bytes": 50_000_000})
    assert m7 is not None and "T1048" in m7["mitre_techniques"]

    r8 = detection_registry.get_rule("RULE-008")
    m8 = r8.evaluate({"destination_port": 88, "attack_type": "Kerberoasting", "is_malicious": True})
    assert m8 is not None and "T1558" in m8["mitre_techniques"]

    r9 = detection_registry.get_rule("RULE-009")
    m9 = r9.evaluate({"attack_type": "PortScan"})
    assert m9 is not None and "T1046" in m9["mitre_techniques"]

    r10 = detection_registry.get_rule("RULE-010")
    m10 = r10.evaluate({"attack_type": "DDoS", "flow_rate_packets_per_sec": 5000.0})
    assert m10 is not None and "T1498" in m10["mitre_techniques"]


@pytest.mark.unit
def test_registry_evaluate_all():
    """Verify registry evaluates multiple rules and aggregates matches."""
    event = {
        "source_ip": "10.0.0.100",
        "destination_ip": "10.0.0.200",
        "destination_port": 445,
        "is_malicious": True,
        "matched_iocs": [{"value": "10.0.0.200", "severity": "HIGH", "confidence": 0.90}],
        "attack_type": "PortScan"
    }
    matches = detection_registry.evaluate_all(event)
    assert len(matches) >= 2
    matched_ids = {m["rule_id"] for m in matches}
    assert "RULE-003" in matched_ids  # IOC
    assert "RULE-004" in matched_ids  # SMB 445
    assert "RULE-009" in matched_ids  # PortScan
