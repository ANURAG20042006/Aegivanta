"""
backend/app/services/edge_inspection_service.py
===============================================
Phase 41 Edge Inspection Policy & DDoS Scrubbing Service.
Evaluates edge-side rate limiting, geo-fencing, and inline packet inspection.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.edge_security_fabric import EdgeInspectionPolicy

logger = logging.getLogger("Aegivanta.EdgeInspection")


class EdgeInspectionService:
    """Enterprise Edge Inspection & DDoS Mitigation Engine."""

    @classmethod
    async def list_policies(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active edge inspection policies."""
        stmt = select(EdgeInspectionPolicy).where(
            EdgeInspectionPolicy.tenant_id == tenant_id
        ).order_by(desc(EdgeInspectionPolicy.created_at)).limit(limit)

        policies = list((await db.execute(stmt)).scalars().all())

        if not policies:
            defaults = [
                ("Global Autonomous L7 DDoS Scrubbing Policy", "SCRUB_DDOS", 100000, "BLOCK", True),
                ("High-Velocity Telemetry Rate Limiter", "INLINE_BLOCK", 50000, "CHALLENGE", True),
                ("Geo-Fencing Sanctioned Territory Ingress Blocker", "INLINE_BLOCK", 25000, "BLOCK", True)
            ]
            for name, mode, rlimit, gact, enab in defaults:
                inst = EdgeInspectionPolicy(
                    tenant_id=tenant_id,
                    policy_name=name,
                    inspection_mode=mode,
                    edge_rate_limit_rps=rlimit,
                    geo_fence_action=gact,
                    enabled=enab,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(EdgeInspectionPolicy).where(EdgeInspectionPolicy.tenant_id == tenant_id)
            policies = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": p.id,
                "policy_name": p.policy_name,
                "inspection_mode": p.inspection_mode,
                "edge_rate_limit_rps": p.edge_rate_limit_rps,
                "geo_fence_action": p.geo_fence_action,
                "enabled": p.enabled,
                "created_at": p.created_at.isoformat()
            }
            for p in policies
        ]

    @classmethod
    async def create_policy(
        cls,
        db: AsyncSession,
        tenant_id: str,
        policy_name: str,
        inspection_mode: str = "INLINE_BLOCK",
        edge_rate_limit_rps: int = 50000,
        geo_fence_action: str = "CHALLENGE"
    ) -> Dict[str, Any]:
        """Deploys a new edge inspection & DDoS mitigation policy."""
        policy = EdgeInspectionPolicy(
            tenant_id=tenant_id,
            policy_name=policy_name,
            inspection_mode=inspection_mode,
            edge_rate_limit_rps=edge_rate_limit_rps,
            geo_fence_action=geo_fence_action,
            enabled=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(policy)
        await db.flush()

        return {
            "id": policy.id,
            "policy_name": policy.policy_name,
            "inspection_mode": policy.inspection_mode,
            "edge_rate_limit_rps": policy.edge_rate_limit_rps,
            "geo_fence_action": policy.geo_fence_action,
            "enabled": policy.enabled,
            "created_at": policy.created_at.isoformat()
        }
