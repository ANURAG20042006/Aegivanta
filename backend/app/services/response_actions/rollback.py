"""
backend/app/services/response_actions/rollback.py
=================================================
Phase 3.7 SOAR Action Rollback Engine.
"""

from typing import Dict, Any, Optional
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.response import ResponseActionRecord, is_valid_action_transition
from backend.app.models.incident_timeline import IncidentTimelineEvent

logger = logging.getLogger("SentinelAI")


class ResponseRollbackService:
    """Coordinates reversible rollback for executed SOAR actions."""

    @classmethod
    async def rollback_action(
        cls,
        action_record_id: str,
        rolled_back_by: str,
        action_registry: Any,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Rolls back an executed action record."""
        res = await db.execute(select(ResponseActionRecord).where(ResponseActionRecord.id == action_record_id))
        action = res.scalar_one_or_none()
        if not action:
            raise LookupError(f"Response action record '{action_record_id}' not found.")

        if action.status not in ["SUCCEEDED", "FAILED", "ROLLBACK_REQUIRED"]:
            raise ValueError(f"Action in status '{action.status}' cannot be rolled back.")

        handler = action_registry.get_action(action.action_type)
        if not handler or not handler.is_reversible:
            action.rollback_status = "ROLLBACK_UNAVAILABLE"
            await db.commit()
            return {
                "status": "ROLLBACK_UNAVAILABLE",
                "action_id": action.id,
                "reason": f"Action type '{action.action_type}' is not reversible."
            }

        action.status = "ROLLING_BACK"
        await db.flush()

        reversal_state = (action.execution_result or {}).get("reversal_state", {})
        rb_res = await handler.rollback(action.target_entity, reversal_state)

        if rb_res.get("status") in ["ROLLED_BACK", "SUCCEEDED"]:
            action.status = "ROLLED_BACK"
            action.rollback_status = "COMPLETED"

            # Record timeline event
            tl = IncidentTimelineEvent(
                incident_id=action.incident_id,
                event_type="REMEDIATION",
                title=f"Rollback Completed: {action.action_type}",
                description=f"Action '{action.action_type}' on target '{action.target_entity}' was rolled back by {rolled_back_by}.",
                actor=rolled_back_by,
                metadata_payload={"action_id": action.id, "rollback_result": rb_res}
            )
            db.add(tl)
            await db.commit()
            await db.refresh(action)
            logger.info("Successfully rolled back action %s on target %s", action.id, action.target_entity)
            return {
                "status": "ROLLED_BACK",
                "action_id": action.id,
                "details": rb_res.get("details", {})
            }
        else:
            action.status = "FAILED"
            action.rollback_status = "FAILED"
            await db.commit()
            return {
                "status": "FAILED",
                "action_id": action.id,
                "reason": "Rollback execution failed on target infrastructure."
            }
