"""
backend/app/services/threat_feed_worker.py
==========================================
Phase 3.4 Asynchronous Threat Feed Synchronization Worker Daemon.
Handles automated background synchronization of configured external/internal threat
intelligence feeds, automated IOC lifecycle pruning, and cache refreshing.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import AsyncSessionLocal
from backend.app.models.threat_intel import ThreatFeed, ThreatIndicator
from backend.app.services.threat_intel_service import ThreatIntelService
from backend.app.core.logging import logger


class ThreatFeedSyncWorker:
    """
    Background worker daemon that polls active threat feeds,
    ingests updated indicators, prunes expired IOCs, and refreshes the fast cache.
    """

    def __init__(self, poll_interval_seconds: int = 3600):
        self.poll_interval_seconds = poll_interval_seconds
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.sync_cycles_completed: int = 0
        self.feeds_synced_total: int = 0
        self.indicators_synced_total: int = 0
        self.failed_syncs_total: int = 0
        self.last_cycle_timestamp: Optional[datetime] = None
        self.last_prune_timestamp: Optional[datetime] = None

    async def sync_all_active_feeds(self, db: AsyncSession) -> Dict[str, Any]:
        """Synchronizes all active threat feeds that are due for polling."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        res = await db.execute(select(ThreatFeed).where(ThreatFeed.is_active == True))
        feeds = res.scalars().all()

        synced_count = 0
        imported_total = 0
        failed_count = 0

        for feed in feeds:
            # Check if feed is due for synchronization
            is_due = False
            if not feed.last_synced_at or feed.last_sync_status in ["IDLE", "FAILED"]:
                is_due = True
            elif feed.poll_interval_hours:
                due_time = feed.last_synced_at + timedelta(hours=feed.poll_interval_hours)
                if now >= due_time:
                    is_due = True

            if is_due:
                try:
                    imported = await ThreatIntelService.ingest_feed(feed, db)
                    imported_total += imported
                    synced_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error syncing feed '{feed.feed_name}': {e}")

        await db.commit()

        self.feeds_synced_total += synced_count
        self.indicators_synced_total += imported_total
        self.failed_syncs_total += failed_count
        self.last_cycle_timestamp = now

        return {
            "feeds_evaluated": len(feeds),
            "feeds_synced": synced_count,
            "indicators_imported": imported_total,
            "failures": failed_count
        }

    async def run_cycle(self):
        """Executes a single end-to-end sync, prune, and cache warm-up cycle."""
        async with AsyncSessionLocal() as db:
            try:
                # 1. Sync feeds
                sync_res = await self.sync_all_active_feeds(db)
                # 2. Daily IOC pruning
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                if not self.last_prune_timestamp or (now - self.last_prune_timestamp).total_seconds() > 86400:
                    await ThreatIntelService.prune_expired_iocs(db, max_age_days=90, min_confidence=0.20)
                    self.last_prune_timestamp = now
                    await db.commit()
                # 3. Refresh fast in-memory cache
                all_iocs = await db.execute(select(ThreatIndicator).where(ThreatIndicator.is_active == True))
                ThreatIntelService.cache.warm_up(all_iocs.scalars().all())

                self.sync_cycles_completed += 1
                return sync_res
            except Exception as exc:
                logger.error(f"ThreatFeedSyncWorker cycle error: {exc}")
                raise

    async def start(self):
        """Starts the background polling loop."""
        self.is_running = True
        logger.info("ThreatFeedSyncWorker daemon started.")
        while self.is_running:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"ThreatFeedSyncWorker error: {e}")
            
            try:
                await asyncio.sleep(self.poll_interval_seconds)
            except asyncio.CancelledError:
                break

    def stop(self):
        """Stops the background worker loop."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("ThreatFeedSyncWorker daemon stopped.")

    def get_status(self) -> Dict[str, Any]:
        """Returns runtime health and performance metrics for the worker."""
        return {
            "is_running": self.is_running,
            "poll_interval_seconds": self.poll_interval_seconds,
            "sync_cycles_completed": self.sync_cycles_completed,
            "feeds_synced_total": self.feeds_synced_total,
            "indicators_synced_total": self.indicators_synced_total,
            "failed_syncs_total": self.failed_syncs_total,
            "last_cycle_timestamp": self.last_cycle_timestamp.isoformat() if self.last_cycle_timestamp else None,
            "last_prune_timestamp": self.last_prune_timestamp.isoformat() if self.last_prune_timestamp else None
        }


feed_sync_worker = ThreatFeedSyncWorker()
