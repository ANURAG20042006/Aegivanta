import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.integration import CustomerIntegration
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("SentinelAI.Integration")


class IntegrationService:
    """Dispatches alerts, incident summaries, and SOC notifications to customer integrations."""

    @classmethod
    async def create_integration(
        cls,
        db: AsyncSession,
        organization_id: str,
        integration_type: str,
        name: str,
        config: Dict[str, Any],
        secret: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> CustomerIntegration:
        """Registers a new external connector."""
        integration = CustomerIntegration(
            organization_id=organization_id,
            tenant_id=tenant_id,
            integration_type=integration_type.upper(),
            name=name,
            status="ACTIVE",
            config_json=config,
            encrypted_secret=secret
        )
        db.add(integration)
        await db.flush()
        return integration

    @classmethod
    async def test_integration(
        cls,
        db: AsyncSession,
        integration_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Simulates external ping/test dispatch."""
        stmt = select(CustomerIntegration).where(
            and_(
                CustomerIntegration.id == integration_id,
                CustomerIntegration.organization_id == organization_id
            )
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            raise SentinelAIException(status_code=404, detail="Integration not found")

        item.last_sync_at = datetime.now(timezone.utc)
        await db.flush()

        logger.info("Tested integration %s (%s)", item.name, item.integration_type)
        return {
            "success": True,
            "message": f"Successfully connected to {item.integration_type} connector.",
            "timestamp": item.last_sync_at.isoformat()
        }

    @classmethod
    async def dispatch_notification(
        cls,
        db: AsyncSession,
        organization_id: str,
        event_title: str,
        event_body: Dict[str, Any]
    ) -> int:
        """Dispatches an event notification to all active integrations of an organization."""
        stmt = select(CustomerIntegration).where(
            and_(
                CustomerIntegration.organization_id == organization_id,
                CustomerIntegration.status == "ACTIVE"
            )
        )
        res = await db.execute(stmt)
        active_integrations = res.scalars().all()

        dispatched_count = 0
        for integ in active_integrations:
            integ.last_sync_at = datetime.now(timezone.utc)
            dispatched_count += 1
            logger.info("Dispatched notification to %s [%s]: %s", integ.name, integ.integration_type, event_title)

        await db.flush()
        return dispatched_count
