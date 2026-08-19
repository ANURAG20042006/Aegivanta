"""
tests/integration/test_phase2_telemetry_streaming.py
===================================================
Unit & integration tests for Phase 2 Telemetry Streaming, Idempotency & DLQ Engine.
"""

import pytest
import asyncio
from backend.app.services.stream_service import IdempotentEventStreamer, TelemetryEventStatus


@pytest.mark.asyncio
async def test_idempotent_event_streamer_deduplication():
    """Verify duplicate telemetry events within the deduplication window are rejected."""
    streamer = IdempotentEventStreamer(cache_size=100)

    processed_events = []

    async def sample_processor(payload):
        processed_events.append(payload)
        return {"processed": True}

    payload = {
        "event_id": "EVT-101",
        "features": {
            "source_ip": "198.51.100.10",
            "destination_ip": "10.0.0.1",
            "source_port": 44444,
            "destination_port": 80,
            "protocol": "TCP",
            "flow_duration": 1000.0,
            "total_fwd_packets": 50.0,
            "packet_length_mean": 400.0
        }
    }

    # First Ingestion -> Should Process
    res1 = await streamer.ingest_event(payload, sample_processor)
    assert res1["status"] == TelemetryEventStatus.PROCESSED
    assert len(processed_events) == 1

    # Second Ingestion with Same Payload -> Should be Detected as Duplicate
    res2 = await streamer.ingest_event(payload, sample_processor)
    assert res2["status"] == TelemetryEventStatus.DUPLICATE
    assert len(processed_events) == 1  # No duplicate execution!


@pytest.mark.asyncio
async def test_dead_letter_queue_and_retry_backoff():
    """Verify unrecoverable processing failures are routed to the Dead Letter Queue after max retries."""
    streamer = IdempotentEventStreamer(max_retries=3, retry_delay_ms=10)

    attempt_counter = 0

    async def failing_processor(payload):
        nonlocal attempt_counter
        attempt_counter += 1
        raise ValueError("Simulated parsing failure")

    payload = {
        "event_id": "EVT-FAIL-01",
        "features": {"malformed": "data"}
    }

    res = await streamer.ingest_event(payload, failing_processor)
    assert res["status"] == TelemetryEventStatus.FAILED_DLQ
    assert res["attempts"] == 3
    assert attempt_counter == 3

    # Verify entry in DLQ
    dlq_entries = streamer.get_dlq_entries()
    assert len(dlq_entries) == 1
    assert dlq_entries[0]["event_id"] == "EVT-FAIL-01"
    assert "Simulated parsing failure" in dlq_entries[0]["failure_reason"]

    # Verify metrics
    metrics = streamer.get_stream_metrics()
    assert metrics["total_dlq"] == 1
    assert metrics["dlq_depth"] == 1
