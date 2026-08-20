import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.usage import UsageRecord, UsageQuota

logger = logging.getLogger("SentinelAI.Usage")


class UsageMeteringService:
    """Tracks and meters commercial resource usage per tenant."""

    # In-memory buffer for high-frequency telemetry events
    _buffer: List[Dict[str, Any]] = []
    _lock = asyncio.Lock()

    @classmethod
    async def record_usage_event(
        cls,
        db: AsyncSession,
        tenant_id: str,
        metric_name: str,
        quantity: float = 1.0,
        unit: str = "count",
        resource_id: Optional[str] = None
    ) -> UsageRecord:
        """Persists a single metered event."""
        record = UsageRecord(
            tenant_id=tenant_id,
            metric_name=metric_name,
            quantity=quantity,
            unit=unit,
            resource_id=resource_id,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(record)
        await db.flush()
        return record

    @classmethod
    async def buffer_usage(
        cls,
        tenant_id: str,
        metric_name: str,
        quantity: float = 1.0,
        unit: str = "count"
    ) -> None:
        """Non-blocking memory buffering for high throughput telemetry ingestion."""
        async with cls._lock:
            cls._buffer.append({
                "tenant_id": tenant_id,
                "metric_name": metric_name,
                "quantity": quantity,
                "unit": unit,
                "timestamp": datetime.now(timezone.utc)
            })

    @classmethod
    async def flush_buffer(cls, db: AsyncSession) -> int:
        """Flushes buffered usage records to the database."""
        async with cls._lock:
            if not cls._buffer:
                return 0
            batch = cls._buffer[:]
            cls._buffer.clear()

        records = [
            UsageRecord(
                tenant_id=item["tenant_id"],
                metric_name=item["metric_name"],
                quantity=item["quantity"],
                unit=item["unit"],
                timestamp=item["timestamp"]
            )
            for item in batch
        ]
        db.add_all(records)
        await db.flush()
        return len(records)

    @classmethod
    async def get_monthly_usage_summary(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> Dict[str, float]:
        """Calculates aggregated usage totals for current month."""
        start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        stmt = (
            select(
                UsageRecord.metric_name,
                func.sum(UsageRecord.quantity).label("total_quantity")
            )
            .where(
                and_(
                    UsageRecord.tenant_id == tenant_id,
                    UsageRecord.timestamp >= start_of_month
                )
            )
            .group_by(UsageRecord.metric_name)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return {row[0]: float(row[1] or 0.0) for row in rows}

    @classmethod
    async def check_quota_exceeded(
        cls,
        db: AsyncSession,
        tenant_id: str,
        metric_name: str,
        limit: float
    ) -> Tuple[bool, float]:
        """Returns (is_exceeded, current_usage)."""
        summary = await cls.get_monthly_usage_summary(db, tenant_id)
        current = summary.get(metric_name, 0.0)
        return (current >= limit), current
