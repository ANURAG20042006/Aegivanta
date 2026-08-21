"""
backend/app/services/ztna_controller_service.py
===============================================
Phase 36 Software-Defined Perimeter (SDP) & ZTNA 2.0 Controller Service.
Manages:
- SDP / ZTNA Connector Edge Gateway Fleet
- Identity-bound client access sessions with dynamic trust score attestation
- Session revocation on anomaly detection
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.microsegmentation import ZTNAConnectorNode, ZTNAAccessSession

logger = logging.getLogger("Aegivanta.ZTNAController")


class ZTNAControllerService:
    """Enterprise ZTNA 2.0 & SDP Overlay Controller."""

    @classmethod
    async def list_connectors(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active SDP / ZTNA gateway connector nodes."""
        stmt = select(ZTNAConnectorNode).where(
            ZTNAConnectorNode.tenant_id == tenant_id
        ).order_by(ZTNAConnectorNode.connector_name).limit(limit)

        nodes = list((await db.execute(stmt)).scalars().all())

        if not nodes:
            # Seed default ZTNA connector nodes
            defaults = [
                ("ztna-gw-us-east-1", "us-east-1", "ONLINE", "52.14.88.102", "100.64.0.0/16", 142, 1840.5),
                ("ztna-gw-eu-west-1", "eu-west-1", "ONLINE", "34.240.12.99", "100.65.0.0/16", 98, 920.4),
                ("ztna-gw-ap-southeast-1", "ap-southeast-1", "ONLINE", "13.229.44.18", "100.66.0.0/16", 64, 450.2)
            ]
            for name, reg, stat, ip, cidr, cnt, gb in defaults:
                inst = ZTNAConnectorNode(
                    tenant_id=tenant_id,
                    connector_name=name,
                    region=reg,
                    status=stat,
                    public_ip=ip,
                    private_overlay_cidr=cidr,
                    active_client_sessions_count=cnt,
                    total_bytes_tunneled_gb=gb,
                    version="v36.0.0",
                    last_heartbeat_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(ZTNAConnectorNode).where(ZTNAConnectorNode.tenant_id == tenant_id)
            nodes = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": n.id,
                "connector_name": n.connector_name,
                "region": n.region,
                "status": n.status,
                "public_ip": n.public_ip,
                "private_overlay_cidr": n.private_overlay_cidr,
                "active_client_sessions_count": n.active_client_sessions_count,
                "total_bytes_tunneled_gb": n.total_bytes_tunneled_gb,
                "version": n.version,
                "last_heartbeat_at": n.last_heartbeat_at.isoformat()
            }
            for n in nodes
        ]

    @classmethod
    async def list_sessions(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active identity-bound ZTNA client access sessions."""
        stmt = select(ZTNAAccessSession).where(
            ZTNAAccessSession.tenant_id == tenant_id
        ).order_by(desc(ZTNAAccessSession.started_at)).limit(limit)

        sessions = list((await db.execute(stmt)).scalars().all())

        if not sessions:
            # Seed default ZTNA access sessions
            defaults = [
                ("alex.mercer@corp.internal", "MAC-CORP-M3-8821", "ztna-gw-us-east-1", "100.64.12.84", "k8s-prod-api.internal:6443", 96, "ACTIVE_TUNNEL"),
                ("elena.rostova@corp.internal", "WIN-SEC-DELL-4410", "ztna-gw-eu-west-1", "100.65.4.19", "vault-cluster.internal:8200", 91, "ACTIVE_TUNNEL"),
                ("david.kim@corp.internal", "LINUX-DEV-THINKPAD-09", "ztna-gw-us-east-1", "100.64.88.201", "pg-db-replica.internal:5432", 45, "REVOKED_ANOMALY")
            ]
            for user, dev, gw, ip, app, trust, stat in defaults:
                inst = ZTNAAccessSession(
                    tenant_id=tenant_id,
                    user_email=user,
                    device_id=dev,
                    connector_node_name=gw,
                    client_overlay_ip=ip,
                    target_application=app,
                    current_trust_score=trust,
                    session_status=stat,
                    started_at=datetime.now(timezone.utc),
                    last_activity_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(ZTNAAccessSession).where(ZTNAAccessSession.tenant_id == tenant_id)
            sessions = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": s.id,
                "user_email": s.user_email,
                "device_id": s.device_id,
                "connector_node_name": s.connector_node_name,
                "client_overlay_ip": s.client_overlay_ip,
                "target_application": s.target_application,
                "current_trust_score": s.current_trust_score,
                "session_status": s.session_status,
                "started_at": s.started_at.isoformat(),
                "last_activity_at": s.last_activity_at.isoformat()
            }
            for s in sessions
        ]

    @classmethod
    async def terminate_session(
        cls,
        db: AsyncSession,
        tenant_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Revokes and terminates a ZTNA overlay session."""
        stmt = select(ZTNAAccessSession).where(
            ZTNAAccessSession.id == session_id,
            ZTNAAccessSession.tenant_id == tenant_id
        )
        sess = (await db.execute(stmt)).scalar_one_or_none()
        if not sess:
            return {"error": "Session not found", "success": False}

        sess.session_status = "REVOKED_ANOMALY"
        sess.last_activity_at = datetime.now(timezone.utc)
        await db.flush()

        return {
            "session_id": sess.id,
            "user_email": sess.user_email,
            "session_status": sess.session_status,
            "success": True
        }
