"""
tests/unit/test_threat_feed_worker.py
=====================================
Phase 3.4 Unit Tests: Threat Feed Synchronization Background Worker Daemon.
Verifies feed polling logic, status tracking, resilience against feed errors, and lifecycle.
"""

import pytest
import datetime
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.models.threat_intel import ThreatFeed
from backend.app.services.threat_feed_worker import ThreatFeedSyncWorker


@pytest.mark.unit
def test_threat_feed_worker_initialization():
    """Verify worker initialization and default metrics."""
    worker = ThreatFeedSyncWorker(poll_interval_seconds=1800)
    assert worker.poll_interval_seconds == 1800
    assert worker.is_running is False
    assert worker.sync_cycles_completed == 0

    status = worker.get_status()
    assert status["is_running"] is False
    assert status["poll_interval_seconds"] == 1800
    assert status["feeds_synced_total"] == 0


@pytest.mark.asyncio
async def test_threat_feed_worker_sync_due_feeds():
    """Verify worker synchronizes feeds that are due for polling."""
    worker = ThreatFeedSyncWorker()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    stale_time = now - timedelta(hours=48)

    due_feed = ThreatFeed(
        id="feed-due",
        feed_name="AlienVault OTX High",
        provider_type="generic_json",
        feed_url="https://example.com/feed.json",
        poll_interval_hours=24,
        last_synced_at=stale_time,
        last_sync_status="SUCCESS",
        is_active=True
    )
    fresh_feed = ThreatFeed(
        id="feed-fresh",
        feed_name="Emerging Threats",
        provider_type="generic_json",
        feed_url="https://example.com/fresh.json",
        poll_interval_hours=24,
        last_synced_at=now - timedelta(hours=2),
        last_sync_status="SUCCESS",
        is_active=True
    )

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [due_feed, fresh_feed]
    mock_db.execute.return_value = mock_res

    with patch("backend.app.services.threat_intel_service.ThreatIntelService.ingest_feed", new_callable=AsyncMock) as mock_ingest:
        mock_ingest.return_value = 15
        res = await worker.sync_all_active_feeds(mock_db)

        assert res["feeds_evaluated"] == 2
        assert res["feeds_synced"] == 1
        assert res["indicators_imported"] == 15
        assert res["failures"] == 0
        mock_ingest.assert_called_once_with(due_feed, mock_db)
        assert worker.feeds_synced_total == 1
        assert worker.indicators_synced_total == 15


@pytest.mark.asyncio
async def test_threat_feed_worker_resilient_error_handling():
    """Verify failing feed syncs are counted and do not interrupt subsequent feeds."""
    worker = ThreatFeedSyncWorker()

    failing_feed = ThreatFeed(
        id="feed-fail",
        feed_name="Failing Feed",
        provider_type="generic_json",
        feed_url="https://broken.example.com",
        last_synced_at=None,
        is_active=True
    )
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [failing_feed]
    mock_db.execute.return_value = mock_res

    with patch("backend.app.services.threat_intel_service.ThreatIntelService.ingest_feed", side_effect=Exception("Connection Timeout")):
        res = await worker.sync_all_active_feeds(mock_db)

        assert res["failures"] == 1
        assert worker.failed_syncs_total == 1


@pytest.mark.unit
def test_threat_feed_worker_start_stop():
    """Verify worker start and stop signal handling."""
    worker = ThreatFeedSyncWorker()
    worker.is_running = True
    worker.stop()
    assert worker.is_running is False
