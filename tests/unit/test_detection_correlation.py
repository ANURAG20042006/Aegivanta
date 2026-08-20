"""
tests/unit/test_detection_correlation.py
========================================
Phase 3.6 Unit Tests: Continuous Detection Correlation Engine.
Verifies event aggregation, sliding temporal windows, idempotency, rule matching,
and deterministic correlation bundles.
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.app.services.detection_correlation_service import DetectionCorrelationEngine


@pytest.fixture
def engine():
    eng = DetectionCorrelationEngine(default_window_minutes=15)
    eng.reset()
    return eng


@pytest.mark.unit
def test_correlate_single_malicious_event(engine):
    """Verify single malicious event produces a correlated detection bundle."""
    event = {
        "id": "ev-001",
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.5",
        "destination_port": 445,
        "is_malicious": True,
        "attack_type": "Brute Force",
        "auth_failures": 7,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    bundle = engine.correlate_event(event)
    assert bundle is not None
    assert bundle["event_count"] == 1
    assert bundle["source_ip"] == "192.168.1.100"
    assert bundle["severity"] in ["HIGH", "CRITICAL"]
    assert "T1110.001" in bundle["mitre_techniques"]
    assert bundle["risk_score"] >= 40.0


@pytest.mark.unit
def test_correlation_idempotency_duplicate_event(engine):
    """Verify duplicate event IDs are processed idempotently without duplicates."""
    event = {
        "id": "ev-dup-001",
        "source_ip": "10.0.0.10",
        "destination_ip": "10.0.0.20",
        "is_malicious": True,
        "attack_type": "PortScan"
    }

    b1 = engine.correlate_event(event)
    assert b1 is not None

    b2 = engine.correlate_event(event)
    assert b2 is None  # Skipped as duplicate


@pytest.mark.unit
def test_multi_event_temporal_window_aggregation(engine):
    """Verify multiple events within 15-minute window aggregate into a unified incident cluster."""
    t0 = datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=5)
    t2 = t0 + timedelta(minutes=10)

    events = [
        {"id": "e1", "source_ip": "10.0.0.50", "destination_ip": "10.0.0.1", "is_malicious": True, "attack_type": "PortScan", "timestamp": t0},
        {"id": "e2", "source_ip": "10.0.0.50", "destination_ip": "10.0.0.1", "is_malicious": True, "attack_type": "Brute Force", "auth_failures": 5, "timestamp": t1},
        {"id": "e3", "source_ip": "10.0.0.50", "destination_ip": "10.0.0.1", "destination_port": 445, "is_malicious": True, "timestamp": t2}
    ]

    last_bundle = None
    for ev in events:
        last_bundle = engine.correlate_event(ev, window_minutes=15)

    assert last_bundle is not None
    assert last_bundle["event_count"] == 3
    assert len(last_bundle["matched_rules"]) >= 2
    assert "T1046" in last_bundle["mitre_techniques"]  # PortScan
    assert "T1110.001" in last_bundle["mitre_techniques"]  # Brute Force


@pytest.mark.unit
def test_temporal_window_expiration(engine):
    """Verify events outside temporal window are pruned from correlation."""
    t0 = datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc)
    t_expired = t0 + timedelta(minutes=45)  # Exceeds 15 min window

    e1 = {"id": "old-1", "source_ip": "1.2.3.4", "destination_ip": "5.6.7.8", "is_malicious": True, "timestamp": t0}
    e2 = {"id": "new-1", "source_ip": "1.2.3.4", "destination_ip": "5.6.7.8", "is_malicious": True, "timestamp": t_expired}

    engine.correlate_event(e1, window_minutes=15)
    b2 = engine.correlate_event(e2, window_minutes=15)

    assert b2 is not None
    assert b2["event_count"] == 1
    assert "new-1" in b2["event_ids"]
    assert "old-1" not in b2["event_ids"]
