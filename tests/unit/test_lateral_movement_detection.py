"""
tests/unit/test_lateral_movement_detection.py
=============================================
Phase 3.5 Unit Tests: Multi-Hop Lateral Movement Path Detection Engine.
Verifies causal chaining (A -> B -> C -> D), MITRE ATT&CK mapping, dwell time thresholds,
cumulative risk calculation, and choke point extraction.
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.app.services.lateral_movement_service import LateralMovementDetector


@pytest.mark.unit
def test_classify_port_technique():
    """Verify standard MITRE ATT&CK port-to-technique mapping."""
    tech_id, name, sev = LateralMovementDetector.classify_port_technique(445)
    assert tech_id == "T1021.002"
    assert "SMB" in name
    assert sev == "CRITICAL"

    tech_id, name, sev = LateralMovementDetector.classify_port_technique(3389)
    assert tech_id == "T1021.001"
    assert "RDP" in name

    tech_id, name, sev = LateralMovementDetector.classify_port_technique(22)
    assert tech_id == "T1021.004"
    assert "SSH" in name

    tech_id, name, sev = LateralMovementDetector.classify_port_technique(5985)
    assert tech_id == "T1021.006"
    assert "WinRM" in name

    tech_id, name, sev = LateralMovementDetector.classify_port_technique(88)
    assert tech_id == "T1558"
    assert "Kerberos" in name


@pytest.mark.unit
def test_detect_lateral_movement_3hop_chain():
    """Verify detection of a 3-hop traversal: 10.0.0.5 -> 10.0.0.10 -> 10.0.0.20 -> 10.0.0.100."""
    t0 = datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=15)
    t2 = t1 + timedelta(minutes=30)

    events = [
        {
            "id": "ev-1",
            "source_ip": "10.0.0.5",
            "destination_ip": "10.0.0.10",
            "destination_port": 22,
            "protocol": "TCP",
            "timestamp": t0,
            "risk_score": 75.0,
            "severity": "HIGH"
        },
        {
            "id": "ev-2",
            "source_ip": "10.0.0.10",
            "destination_ip": "10.0.0.20",
            "destination_port": 445,
            "protocol": "TCP",
            "timestamp": t1,
            "risk_score": 85.0,
            "severity": "CRITICAL"
        },
        {
            "id": "ev-3",
            "source_ip": "10.0.0.20",
            "destination_ip": "10.0.0.100",
            "destination_port": 3389,
            "protocol": "TCP",
            "timestamp": t2,
            "risk_score": 90.0,
            "severity": "CRITICAL"
        }
    ]

    chains = LateralMovementDetector.detect_lateral_movement_chains(events, max_dwell_hours=24.0, min_chain_length=2)

    assert len(chains) == 1
    c = chains[0]
    assert c["initial_compromise_host"] == "10.0.0.5"
    assert c["target_host"] == "10.0.0.100"
    assert c["hop_count"] == 3
    assert c["node_sequence"] == ["10.0.0.5", "10.0.0.10", "10.0.0.20", "10.0.0.100"]
    assert c["recommended_chokepoints"] == ["10.0.0.10", "10.0.0.20"]
    assert c["cumulative_risk_score"] > 95.0
    assert c["severity"] == "CRITICAL"
    assert len(c["hops"]) == 3
    assert c["hops"][1]["dwell_time_seconds"] == 900.0  # 15 minutes


@pytest.mark.unit
def test_detect_lateral_movement_dwell_time_exceeded():
    """Verify that hops separated by more than max_dwell_hours do not link into a single chain."""
    t0 = datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(hours=48)  # 48 hours later -> exceeds 24 hour threshold

    events = [
        {
            "id": "ev-1",
            "source_ip": "192.168.1.5",
            "destination_ip": "192.168.1.10",
            "destination_port": 445,
            "timestamp": t0,
            "risk_score": 80.0
        },
        {
            "id": "ev-2",
            "source_ip": "192.168.1.10",
            "destination_ip": "192.168.1.50",
            "destination_port": 3389,
            "timestamp": t1,
            "risk_score": 85.0
        }
    ]

    chains = LateralMovementDetector.detect_lateral_movement_chains(events, max_dwell_hours=24.0, min_chain_length=2)
    assert len(chains) == 0


@pytest.mark.unit
def test_detect_lateral_movement_empty_and_single_hop():
    """Verify edge cases with 0 or 1 event."""
    assert LateralMovementDetector.detect_lateral_movement_chains([]) == []
    assert LateralMovementDetector.detect_lateral_movement_chains([
        {"source_ip": "1.1.1.1", "destination_ip": "2.2.2.2", "timestamp": datetime.now(timezone.utc)}
    ]) == []
