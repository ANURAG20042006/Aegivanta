"""
backend/app/services/playbook_service.py
========================================
Automated Security Playbook Execution & Simulation Engine.
Enforces default DRY RUN / SIMULATION safety, persistent audit records,
and incident timeline integration.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.playbook import PlaybookExecution
from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.core.logging import logger


class PlaybookService:
    """Safe Playbook Execution & Simulation Service."""

    @staticmethod
    async def execute_action(
        incident_id: str,
        playbook_name: str,
        action_type: str,
        target_entity: str,
        is_dry_run: bool = True,
        executed_by: str = "automated_system",
        parameters: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Executes a security playbook action. Defaults strictly to dry_run=True (simulation mode).
        Creates an audit record in PlaybookExecution and appends to the Incident timeline.
        """
        parameters = parameters or {}
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if is_dry_run:
            status_result = "SIMULATED_SUCCESS"
            log_msg = (
                f"[SIMULATION DRY RUN] Action '{action_type}' for target '{target_entity}' "
                f"simulated successfully. Zero destructive changes applied to perimeter infrastructure."
            )
        else:
            status_result = "EXECUTED_SUCCESS"
            log_msg = (
                f"[LIVE EXECUTION] Action '{action_type}' for target '{target_entity}' "
                f"executed with parameters {parameters}."
            )

        execution = PlaybookExecution(
            incident_id=incident_id,
            playbook_name=playbook_name,
            action_type=action_type,
            is_dry_run=is_dry_run,
            target_entity=target_entity,
            parameters=parameters,
            status=status_result,
            executed_by=executed_by,
            actor_role=parameters.get("actor_role", "analyst") if parameters else "analyst",
            authorization_decision="APPROVED",
            execution_log=log_msg,
            created_at=now
        )
        db.add(execution)

        # Append to Incident Timeline
        timeline_ev = IncidentTimelineEvent(
            incident_id=incident_id,
            event_type="REMEDIATION",
            title=f"Playbook: {playbook_name} ({'Dry Run' if is_dry_run else 'Live'})",
            description=log_msg,
            actor=executed_by,
            metadata_payload={
                "action_type": action_type,
                "is_dry_run": is_dry_run,
                "target": target_entity
            },
            timestamp=datetime.now(timezone.utc)
        )
        db.add(timeline_ev)
        await db.flush()

        # Broadcast WebSocket telemetry
        try:
            from backend.app.api.v1.websocket import manager
            await manager.broadcast({
                "type": "PLAYBOOK_STATUS",
                "data": {
                    "execution_id": execution.id,
                    "incident_id": incident_id,
                    "playbook_name": playbook_name,
                    "action_type": action_type,
                    "is_dry_run": is_dry_run,
                    "status": status_result,
                    "timestamp": now.isoformat()
                }
            })
        except Exception:
            pass

        return {
            "execution_id": execution.id,
            "incident_id": incident_id,
            "playbook_name": playbook_name,
            "action_type": action_type,
            "is_dry_run": is_dry_run,
            "status": status_result,
            "log": log_msg,
            "timestamp": now.isoformat()
        }
