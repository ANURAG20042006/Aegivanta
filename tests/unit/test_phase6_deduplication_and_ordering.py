"""
tests/unit/test_phase6_deduplication_and_ordering.py
====================================================
Unit tests for Telemetry Event Deduplication and Sequence Sorting.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.telemetry_ingestion_service import TelemetryIngestionService
from backend.app.models.sensor import Sensor


@pytest.mark.asyncio
async def test_duplicate_event_suppression():
    """Identical telemetry events from the same sensor must be deduplicated."""
    db = AsyncMock()
    mock_sensor = Sensor(id="sen-test", tenant_id="ten-test", status="ONLINE")

    event = {
        "event_type": "DNS_QUERY",
        "seq_id": 1,
        "data": {"query_name": "unique-dns-query.org", "query_type": "A"}
    }

    batch_1 = {"schema_version": "v1", "events": [event]}
    batch_2 = {"schema_version": "v1", "events": [event]}  # Duplicate

    res1 = await TelemetryIngestionService.process_telemetry_batch(db, mock_sensor, batch_1)
    assert res1["events_processed"] == 1
    assert res1["duplicates_suppressed"] == 0

    res2 = await TelemetryIngestionService.process_telemetry_batch(db, mock_sensor, batch_2)
    assert res2["events_processed"] == 0
    assert res2["duplicates_suppressed"] == 1
