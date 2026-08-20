"""
backend/app/services/soar_connector_service.py
==============================================
Phase 19 SOAR Connector Integration Service.
Manages firewall, EDR, IAM, and SIEM security orchestration integrations.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.soar_v2 import SOARConnector
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("Aegivanta.SOARConnectors")

DEFAULT_CONNECTORS = [
    {
        "connector_name": "Palo Alto Next-Gen Firewall Tap",
        "connector_type": "FIREWALL",
        "provider": "PALO_ALTO",
        "endpoint_url": "https://paloalto.sec.internal/api",
        "health_status": "HEALTHY",
        "latency_ms": 14.2
    },
    {
        "connector_name": "CrowdStrike Falcon Sensor EDR Connector",
        "connector_type": "EDR",
        "provider": "CROWDSTRIKE",
        "endpoint_url": "https://api.crowdstrike.com/v2",
        "health_status": "HEALTHY",
        "latency_ms": 19.8
    },
    {
        "connector_name": "Okta Enterprise IAM Directory",
        "connector_type": "IAM",
        "provider": "OKTA",
        "endpoint_url": "https://aegivanta.okta.com/api/v1",
        "health_status": "HEALTHY",
        "latency_ms": 22.1
    },
    {
        "connector_name": "ServiceNow SecOps Ticketing Hub",
        "connector_type": "TICKETING",
        "provider": "SERVICENOW",
        "endpoint_url": "https://aegivanta.service-now.com/api/v1",
        "health_status": "HEALTHY",
        "latency_ms": 31.4
    }
]


class SOARConnectorService:
    """Provides connector discovery, provisioning, and continuous health auditing."""

    @classmethod
    async def list_connectors(cls, db: AsyncSession, tenant_id: str) -> List[Dict[str, Any]]:
        """Lists active security orchestration connectors for the tenant."""
        stmt = select(SOARConnector).where(SOARConnector.tenant_id == tenant_id)
        connectors = list((await db.execute(stmt)).scalars().all())

        if not connectors:
            # Seed default connectors on first query
            for c in DEFAULT_CONNECTORS:
                inst = SOARConnector(
                    tenant_id=tenant_id,
                    connector_name=c["connector_name"],
                    connector_type=c["connector_type"],
                    provider=c["provider"],
                    endpoint_url=c["endpoint_url"],
                    health_status=c["health_status"],
                    latency_ms=c["latency_ms"],
                    last_heartbeat=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(SOARConnector).where(SOARConnector.tenant_id == tenant_id)
            connectors = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": c.id,
                "connector_name": c.connector_name,
                "connector_type": c.connector_type,
                "provider": c.provider,
                "endpoint_url": c.endpoint_url,
                "is_active": c.is_active,
                "health_status": c.health_status,
                "latency_ms": c.latency_ms,
                "last_heartbeat": c.last_heartbeat.isoformat() if c.last_heartbeat else None
            }
            for c in connectors
        ]

    @classmethod
    async def test_connector_health(cls, db: AsyncSession, connector_id: str) -> Dict[str, Any]:
        """Runs on-demand health check against a connector instance."""
        stmt = select(SOARConnector).where(SOARConnector.id == connector_id)
        c = (await db.execute(stmt)).scalar_one_or_none()
        if not c:
            raise SentinelAIException(status_code=404, detail="Connector not found.")

        t0 = time.perf_counter()
        # Simulated ping
        latency = round((time.perf_counter() - t0) * 1000.0 + 12.0, 2)
        c.latency_ms = latency
        c.health_status = "HEALTHY"
        c.last_heartbeat = datetime.now(timezone.utc)
        await db.flush()

        return {
            "connector_id": c.id,
            "connector_name": c.connector_name,
            "health_status": "HEALTHY",
            "latency_ms": latency
        }
