"""
tests/unit/test_phase4_usage.py
===============================
Unit tests for Phase 4 Telemetry Usage Metering and Quotas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.usage_metering_service import UsageMeteringService


@pytest.mark.asyncio
async def test_usage_metering_buffer_and_flush():
    """Validates non-blocking in-memory usage buffering and batch flushing."""
    db = AsyncMock()
    db.add_all = MagicMock()
    db.flush = AsyncMock()

    # Buffer 3 events
    await UsageMeteringService.buffer_usage("ten-1", "events_ingested", 100.0)
    await UsageMeteringService.buffer_usage("ten-1", "events_ingested", 250.0)
    await UsageMeteringService.buffer_usage("ten-2", "api_requests", 1.0)

    flushed_count = await UsageMeteringService.flush_buffer(db)
    assert flushed_count == 3
    db.add_all.assert_called_once()
