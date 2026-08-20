import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.tenant import TenantSettings, Tenant
from backend.app.models.security_event import SecurityEvent
from backend.app.models.alert import Alert
from backend.app.models.usage import UsageRecord
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType

logger = logging.getLogger("SentinelAI.Retention")


class TenantRetentionService:
    """Enforces tenant-specific data retention schedules (Hot/Warm/Purge) with audit trails."""

    @classmethod
    async def apply_retention_policy(
        cls,
        db: AsyncSession,
        tenant_id: str,
        actor_id: str = "system"
    ) -> Dict[str, Any]:
        """Applies configured retention period for a tenant and purges expired records."""
        stmt = select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
        res = await db.execute(stmt)
        settings = res.scalar_one_or_none()

        retention_days = settings.retention_days_hot if settings else 30
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        # 1. Purge expired usage records older than retention window
        stmt_usage = select(UsageRecord).where(
            and_(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.timestamp < cutoff_date
            )
        )
        res_usage = await db.execute(stmt_usage)
        expired_usage = res_usage.scalars().all()
        purged_usage_count = len(expired_usage)
        for u in expired_usage:
            await db.delete(u)

        # 2. Immutable Audit Record
        await ImmutableAuditService.record(
            db=db,
            event_type=AuditEventType.RETENTION_APPLIED,
            actor_id=actor_id,
            resource=f"tenant:{tenant_id}",
            action=f"Applied retention policy: {retention_days} days cutoff ({cutoff_date.date()})",
            details={
                "retention_days": retention_days,
                "purged_records": purged_usage_count,
                "cutoff": cutoff_date.isoformat()
            }
        )

        await db.flush()
        logger.info("Applied retention policy for tenant %s: purged %d records", tenant_id, purged_usage_count)
        return {
            "tenant_id": tenant_id,
            "retention_days": retention_days,
            "cutoff_timestamp": cutoff_date.isoformat(),
            "purged_records": purged_usage_count,
            "status": "COMPLETED"
        }
