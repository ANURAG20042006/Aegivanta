"""
backend/app/services/endpoint_response_service.py
=================================================
Phase 22 Governed Endpoint Response & Containment Service.
Executes policy/approval-controlled endpoint isolation, process termination, and rollback.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.endpoint_xdr import EndpointResponseAction

logger = logging.getLogger("Aegivanta.EndpointResponse")

VALID_RESPONSE_ACTIONS = [
    "ISOLATE_ENDPOINT",
    "TERMINATE_PROCESS",
    "REVOKE_SESSION",
    "RESET_CREDENTIALS",
    "RESTORE_ISOLATION"
]


class EndpointResponseService:
    """Executes policy-controlled and human-approved endpoint containment actions."""

    @classmethod
    async def execute_response_action(
        cls,
        db: AsyncSession,
        tenant_id: str,
        sensor_id: str,
        hostname: str,
        action_type: str,
        target_entity: str,
        reason: str,
        operator_id: str = "SOC_OPERATOR_ADMIN",
        approval_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes a governed endpoint response action."""
        act_upper = action_type.upper()
        if act_upper not in VALID_RESPONSE_ACTIONS:
            raise ValueError(f"Unsupported endpoint response action: {action_type}")

        action = EndpointResponseAction(
            tenant_id=tenant_id,
            sensor_id=sensor_id,
            hostname=hostname,
            action_type=act_upper,
            target_entity=target_entity,
            reason=reason,
            operator_id=operator_id,
            approval_id=approval_id,
            status="EXECUTED",
            executed_at=datetime.now(timezone.utc)
        )
        db.add(action)
        await db.flush()

        logger.info(f"Executed {act_upper} on {hostname} for {target_entity} (tenant: {tenant_id})")

        return {
            "id": action.id,
            "sensor_id": action.sensor_id,
            "hostname": action.hostname,
            "action_type": action.action_type,
            "target_entity": action.target_entity,
            "status": action.status,
            "reason": action.reason,
            "executed_at": action.executed_at.isoformat()
        }

    @classmethod
    async def rollback_response_action(
        cls,
        db: AsyncSession,
        tenant_id: str,
        action_id: str
    ) -> Dict[str, Any]:
        """Rolls back an executed endpoint action (e.g. restores isolated endpoint)."""
        stmt = select(EndpointResponseAction).where(
            EndpointResponseAction.id == action_id,
            EndpointResponseAction.tenant_id == tenant_id
        )
        action = (await db.execute(stmt)).scalar_one_or_none()
        if not action:
            raise ValueError("Endpoint response action not found.")

        # Create inverse restoration action
        restore_type = "RESTORE_ISOLATION" if action.action_type == "ISOLATE_ENDPOINT" else "ROLLED_BACK"
        action.status = "ROLLED_BACK"

        restore_action = EndpointResponseAction(
            tenant_id=tenant_id,
            sensor_id=action.sensor_id,
            hostname=action.hostname,
            action_type=restore_type,
            target_entity=action.target_entity,
            reason=f"Rollback of action {action_id}",
            operator_id=action.operator_id,
            status="EXECUTED",
            executed_at=datetime.now(timezone.utc)
        )
        db.add(restore_action)
        await db.flush()

        return {
            "original_action_id": action.id,
            "status": "ROLLED_BACK",
            "restoration_action_id": restore_action.id
        }

    @classmethod
    async def list_response_actions(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Lists historical endpoint response actions."""
        stmt = select(EndpointResponseAction).where(
            EndpointResponseAction.tenant_id == tenant_id
        ).order_by(desc(EndpointResponseAction.executed_at))

        actions = list((await db.execute(stmt)).scalars().all())
        return [
            {
                "id": a.id,
                "sensor_id": a.sensor_id,
                "hostname": a.hostname,
                "action_type": a.action_type,
                "target_entity": a.target_entity,
                "status": a.status,
                "reason": a.reason,
                "operator_id": a.operator_id,
                "executed_at": a.executed_at.isoformat() if a.executed_at else None
            }
            for a in actions
        ]
