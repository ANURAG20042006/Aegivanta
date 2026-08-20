"""
tests/unit/test_soc_event_broadcaster.py
========================================
Unit tests for SOCEventBroadcaster: event publication, ring buffering,
duplicate protection, sequence ordering, and payload validation.
"""

import pytest
import asyncio
from backend.app.services.soc_event_broadcaster import (
    SOCEventBroadcaster,
    broadcast_soc_event,
    SOC_EVENT_TYPES
)


@pytest.mark.asyncio
async def test_broadcaster_event_creation_and_buffer():
    broadcaster = SOCEventBroadcaster(max_buffer_size=10)
    broadcaster.clear_buffer()

    evt = await broadcaster.broadcast_event(
        event_type="NEW_INCIDENT",
        title="DDoS Attack Detected",
        description="High volume SYN flood from 192.168.1.105",
        severity="CRITICAL",
        metadata={"incident_id": "INC-001", "ip": "192.168.1.105"},
        publish_to_redis=False
    )

    assert evt["event_id"] is not None
    assert evt["sequence"] == 1
    assert evt["type"] == "NEW_INCIDENT"
    assert evt["severity"] == "CRITICAL"
    assert evt["title"] == "DDoS Attack Detected"
    assert broadcaster.buffer_size == 1

    recent = broadcaster.get_recent_events(limit=5)
    assert len(recent) == 1
    assert recent[0]["event_id"] == evt["event_id"]


@pytest.mark.asyncio
async def test_broadcaster_duplicate_suppression():
    broadcaster = SOCEventBroadcaster(max_buffer_size=10)
    broadcaster.clear_buffer()

    evt1 = await broadcaster.broadcast_event(
        event_type="THREAT_INTEL_MATCH",
        title="IOC Hit",
        description="Malicious IP matched",
        severity="HIGH",
        event_id="FIXED-ID-123",
        publish_to_redis=False
    )
    assert evt1["event_id"] == "FIXED-ID-123"
    assert broadcaster.buffer_size == 1

    # Attempt second broadcast with same event_id
    evt2 = await broadcaster.broadcast_event(
        event_type="THREAT_INTEL_MATCH",
        title="IOC Hit Duplicate",
        description="Malicious IP matched duplicate",
        severity="HIGH",
        event_id="FIXED-ID-123",
        publish_to_redis=False
    )
    assert evt2.get("status") == "DUPLICATE_SUPPRESSED"
    assert broadcaster.buffer_size == 1


@pytest.mark.asyncio
async def test_broadcaster_ring_buffer_capacity():
    broadcaster = SOCEventBroadcaster(max_buffer_size=3)
    broadcaster.clear_buffer()

    for i in range(5):
        await broadcaster.broadcast_event(
            event_type="SYSTEM_ALERT",
            title=f"Alert #{i}",
            description=f"Description #{i}",
            publish_to_redis=False
        )

    # Buffer capped at max_buffer_size=3
    assert broadcaster.buffer_size == 3
    recent = broadcaster.get_recent_events(limit=10)
    assert len(recent) == 3
    # Newest should be sequence 5, 4, 3
    assert recent[0]["title"] == "Alert #4"
    assert recent[1]["title"] == "Alert #3"
    assert recent[2]["title"] == "Alert #2"


@pytest.mark.asyncio
async def test_broadcaster_filter_by_type_and_severity():
    broadcaster = SOCEventBroadcaster(max_buffer_size=10)
    broadcaster.clear_buffer()

    await broadcaster.broadcast_event(
        event_type="NEW_DETECTION",
        title="Port Scan",
        description="Port scanning activity",
        severity="MEDIUM",
        publish_to_redis=False
    )
    await broadcaster.broadcast_event(
        event_type="LATERAL_MOVEMENT_DETECTION",
        title="Lateral Movement",
        description="Host hop detected",
        severity="CRITICAL",
        publish_to_redis=False
    )
    await broadcaster.broadcast_event(
        event_type="RESPONSE_ACTION_EXECUTED",
        title="Host Isolated",
        description="Simulated host isolation",
        severity="HIGH",
        publish_to_redis=False
    )

    crit_events = broadcaster.get_recent_events(severity="CRITICAL")
    assert len(crit_events) == 1
    assert crit_events[0]["type"] == "LATERAL_MOVEMENT_DETECTION"

    resp_events = broadcaster.get_recent_events(event_type="RESPONSE_ACTION_EXECUTED")
    assert len(resp_events) == 1
    assert resp_events[0]["title"] == "Host Isolated"


def test_all_12_soc_event_types_defined():
    expected_12 = [
        "NEW_DETECTION",
        "NEW_INCIDENT",
        "INCIDENT_SEVERITY_ESCALATION",
        "INCIDENT_STATUS_CHANGE",
        "THREAT_INTEL_MATCH",
        "LATERAL_MOVEMENT_DETECTION",
        "RESPONSE_ACTION_REQUESTED",
        "RESPONSE_ACTION_APPROVED",
        "RESPONSE_ACTION_EXECUTED",
        "RESPONSE_ROLLBACK",
        "INVESTIGATION_UPDATE",
        "SYSTEM_ALERT"
    ]
    for et in expected_12:
        assert et in SOC_EVENT_TYPES
