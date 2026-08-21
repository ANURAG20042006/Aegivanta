"""
backend/app/services/edge_fabric_service.py
===========================================
Phase 41 Global Distributed Edge Security & Ingestion Fabric Service.
Manages global edge PoPs, throughput metrics, and regional ingestion routes.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.edge_security_fabric import GlobalEdgePoPNode, RegionalIngestionRoute

logger = logging.getLogger("Aegivanta.EdgeFabric")


class EdgeFabricService:
    """Enterprise Global Edge Ingestion Fabric Engine."""

    @classmethod
    async def list_pops(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active global edge PoP ingestion nodes."""
        stmt = select(GlobalEdgePoPNode).where(
            GlobalEdgePoPNode.tenant_id == tenant_id
        ).order_by(desc(GlobalEdgePoPNode.throughput_gbps)).limit(limit)

        pops = list((await db.execute(stmt)).scalars().all())

        if not pops:
            # Seed default global edge PoPs
            defaults = [
                ("US_EAST_VA", "Ashburn, Virginia (US-East)", "HEALTHY", 84.5, 245000, 3.8),
                ("EU_CENTRAL_FRA", "Frankfurt, Germany (EU-Central)", "HEALTHY", 62.1, 182000, 4.1),
                ("AP_SOUTHEAST_SIN", "Singapore (AP-Southeast)", "HEALTHY", 51.8, 149000, 5.2),
                ("SA_EAST_SAO", "São Paulo, Brazil (SA-East)", "HEALTHY", 28.4, 76000, 8.4)
            ]
            for rcode, loc, stat, tp, conn, lat in defaults:
                inst = GlobalEdgePoPNode(
                    tenant_id=tenant_id,
                    region_code=rcode,
                    pop_location_name=loc,
                    edge_status=stat,
                    throughput_gbps=tp,
                    active_connections=conn,
                    latency_ms=lat,
                    last_heartbeat=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(GlobalEdgePoPNode).where(GlobalEdgePoPNode.tenant_id == tenant_id)
            pops = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": p.id,
                "region_code": p.region_code,
                "pop_location_name": p.pop_location_name,
                "edge_status": p.edge_status,
                "throughput_gbps": p.throughput_gbps,
                "active_connections": p.active_connections,
                "latency_ms": p.latency_ms,
                "last_heartbeat": p.last_heartbeat.isoformat()
            }
            for p in pops
        ]

    @classmethod
    async def list_routes(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists regional ingestion routes to primary core clusters."""
        stmt = select(RegionalIngestionRoute).where(
            RegionalIngestionRoute.tenant_id == tenant_id
        ).order_by(desc(RegionalIngestionRoute.updated_at)).limit(limit)

        routes = list((await db.execute(stmt)).scalars().all())

        if not routes:
            defaults = [
                ("US_EAST_VA", "Core-Cluster-Primary-East", "WIREGUARD_MTLS", 1.2, True),
                ("EU_CENTRAL_FRA", "Core-Cluster-Primary-EU", "WIREGUARD_MTLS", 1.5, True),
                ("AP_SOUTHEAST_SIN", "Core-Cluster-Primary-APAC", "WIREGUARD_MTLS", 1.8, True)
            ]
            for src, tgt, proto, lag, isprim in defaults:
                inst = RegionalIngestionRoute(
                    tenant_id=tenant_id,
                    source_region=src,
                    target_core_cluster=tgt,
                    routing_protocol=proto,
                    replication_lag_ms=lag,
                    is_primary=isprim,
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(RegionalIngestionRoute).where(RegionalIngestionRoute.tenant_id == tenant_id)
            routes = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": r.id,
                "source_region": r.source_region,
                "target_core_cluster": r.target_core_cluster,
                "routing_protocol": r.routing_protocol,
                "replication_lag_ms": r.replication_lag_ms,
                "is_primary": r.is_primary,
                "updated_at": r.updated_at.isoformat()
            }
            for r in routes
        ]
