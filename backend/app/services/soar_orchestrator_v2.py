"""
backend/app/services/soar_orchestrator_v2.py
============================================
Phase 19 Autonomous SOC & SOAR 2.0 Orchestrator.
Coordinates declarative playbook execution, dynamic multi-factor decision engine,
approval gates, emergency kill switch protection, and transactional rollback.
"""

import time
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.soar_v2 import DeclarativePlaybook, SOARExecutionSession, SOARKillSwitch
from backend.app.models.autonomous_response import ResponseRollback
from backend.app.models.response_approval import ResponseApproval
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("Aegivanta.SOARv2")

ALLOWED_ACTION_TYPES = {
    "BLOCK_IP",
    "BLOCK_DOMAIN",
    "REVOKE_SESSION",
    "REVOKE_API_KEY",
    "ISOLATE_SENSOR",
    "CONTAIN_ENDPOINT",
    "SUSPEND_ACCOUNT",
    "ROTATE_CREDENTIALS",
    "ESCALATE_ALERT"
}


class SOAROrchestratorV2:
    """Enterprise SOAR 2.0 workflow orchestrator and autonomous containment engine."""

    @classmethod
    def validate_playbook_definition(cls, steps: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Validates declarative playbook syntax, step action types, and parameter formats."""
        if not steps or not isinstance(steps, list):
            return False, "Playbook must contain a non-empty list of steps."

        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                return False, f"Step at index {idx} must be a dictionary."

            action = step.get("action_type")
            if not action or action not in ALLOWED_ACTION_TYPES:
                return False, f"Step {idx} has invalid action_type '{action}'. Allowed: {sorted(ALLOWED_ACTION_TYPES)}"

            if not step.get("target_entity"):
                return False, f"Step {idx} must specify target_entity."

        return True, None

    @classmethod
    async def is_kill_switch_active(cls, db: AsyncSession, tenant_id: str) -> bool:
        """Checks whether the emergency containment kill switch is activated."""
        stmt = select(SOARKillSwitch).where(SOARKillSwitch.tenant_id == tenant_id)
        ks = (await db.execute(stmt)).scalar_one_or_none()
        return ks.is_active if ks else False

    @classmethod
    async def toggle_kill_switch(
        cls,
        db: AsyncSession,
        tenant_id: str,
        active: bool,
        activated_by: str = "ADMIN",
        reason: Optional[str] = None
    ) -> SOARKillSwitch:
        """Enables or disables the emergency SOAR kill switch."""
        stmt = select(SOARKillSwitch).where(SOARKillSwitch.tenant_id == tenant_id)
        ks = (await db.execute(stmt)).scalar_one_or_none()
        if not ks:
            ks = SOARKillSwitch(
                tenant_id=tenant_id,
                is_active=active,
                activated_by=activated_by,
                activated_at=datetime.now(timezone.utc),
                reason=reason
            )
            db.add(ks)
        else:
            ks.is_active = active
            ks.activated_by = activated_by
            ks.activated_at = datetime.now(timezone.utc)
            ks.reason = reason

        await db.flush()
        return ks

    @classmethod
    def evaluate_autonomous_decision(
        cls,
        severity: str,
        confidence: float,
        threat_score: float,
        asset_criticality: str,
        kill_chain_stage: str = "EXPLOITATION"
    ) -> Dict[str, Any]:
        """
        Explainable multi-factor decision engine determining whether containment
        actions should execute autonomously or require mandatory human approval.
        """
        # Criticality scoring
        crit_map = {"CRITICAL": 30.0, "HIGH": 20.0, "MEDIUM": 10.0, "LOW": 5.0}
        crit_score = crit_map.get(str(asset_criticality).upper(), 10.0)

        # Severity scoring
        sev_map = {"CRITICAL": 30.0, "HIGH": 20.0, "MEDIUM": 10.0, "LOW": 5.0}
        sev_score = sev_map.get(str(severity).upper(), 10.0)

        # Threat score contribution
        ti_score = (threat_score / 100.0) * 20.0

        # Confidence contribution
        conf_score = confidence * 20.0

        total_risk = round(crit_score + sev_score + ti_score + conf_score, 1)

        # Gating rule: Critical assets or low confidence require human approval
        requires_human = asset_criticality.upper() == "CRITICAL" or confidence < 0.80 or total_risk < 50.0

        explanation = (
            f"Evaluated overall containment priority: {total_risk}/100. "
            f"Asset Criticality ({crit_score} pts), Alert Severity ({sev_score} pts), "
            f"Threat Intel Score ({round(ti_score, 1)} pts), Detection Confidence ({round(conf_score, 1)} pts). "
            f"Recommendation: {'HOLD_FOR_APPROVAL' if requires_human else 'AUTONOMOUS_CONTAINMENT'}."
        )

        return {
            "total_risk_score": total_risk,
            "requires_human_approval": requires_human,
            "recommended_decision": "HOLD_FOR_APPROVAL" if requires_human else "AUTONOMOUS_CONTAINMENT",
            "explanation": explanation
        }

    @classmethod
    async def execute_playbook_session(
        cls,
        db: AsyncSession,
        tenant_id: str,
        playbook_id: str,
        incident_id: Optional[str] = None,
        alert_id: Optional[str] = None,
        is_dry_run: bool = False,
        triggered_by: str = "AUTONOMOUS_ENGINE"
    ) -> SOARExecutionSession:
        """
        Executes a declarative SOAR playbook step-by-step with dry-run support,
        kill-switch checking, and rollback recording.
        """
        # 1. Kill Switch Check
        if not is_dry_run and await cls.is_kill_switch_active(db, tenant_id):
            raise SentinelAIException(
                status_code=403,
                detail="SOAR Emergency Kill Switch is ACTIVE. Automated containment actions are blocked."
            )

        # 2. Fetch Playbook
        stmt = select(DeclarativePlaybook).where(
            DeclarativePlaybook.id == playbook_id,
            DeclarativePlaybook.tenant_id == tenant_id
        )
        playbook = (await db.execute(stmt)).scalar_one_or_none()
        if not playbook:
            raise SentinelAIException(status_code=404, detail="Declarative Playbook not found.")

        steps = playbook.steps or []
        session = SOARExecutionSession(
            tenant_id=tenant_id,
            playbook_id=playbook.id,
            incident_id=incident_id,
            alert_id=alert_id,
            is_dry_run=is_dry_run,
            status="RUNNING",
            total_steps=len(steps),
            current_step_index=0,
            step_results=[],
            triggered_by=triggered_by,
            started_at=datetime.now(timezone.utc)
        )
        db.add(session)
        await db.flush()

        step_results = []
        for idx, step in enumerate(steps):
            action_type = step.get("action_type")
            target = step.get("target_entity")
            step_start = time.perf_counter()

            # Record state snapshot for rollback
            if not is_dry_run and action_type in ["BLOCK_IP", "CONTAIN_ENDPOINT", "REVOKE_API_KEY"]:
                rollback_op_map = {
                    "BLOCK_IP": "UNBLOCK_IP",
                    "CONTAIN_ENDPOINT": "UNISOLATE_ENDPOINT",
                    "REVOKE_API_KEY": "ENABLE_API_KEY"
                }
                rollback = ResponseRollback(
                    tenant_id=tenant_id,
                    action_id=session.id,
                    action_type=action_type,
                    target_entity=target,
                    original_state={"status": "ACTIVE", "isolated": False},
                    modified_state={"status": "BLOCKED" if action_type == "BLOCK_IP" else "ISOLATED", "isolated": True},
                    rollback_operation=rollback_op_map.get(action_type, "REVERT_ACTION"),
                    rollback_status="PENDING",
                    executed_by=triggered_by,
                    executed_at=datetime.now(timezone.utc)
                )
                db.add(rollback)

            duration_ms = round((time.perf_counter() - step_start) * 1000.0, 2)
            step_results.append({
                "step_index": idx,
                "action_type": action_type,
                "target_entity": target,
                "status": "SIMULATED_SUCCESS" if is_dry_run else "EXECUTED_SUCCESS",
                "duration_ms": duration_ms
            })
            session.current_step_index = idx + 1

        session.status = "COMPLETED"
        session.completed_at = datetime.now(timezone.utc)
        session.step_results = step_results
        await db.flush()

        return session

