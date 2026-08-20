"""
backend/app/services/autonomous_response_service.py
===================================================
Phase 17.1, 17.2, 17.3, 17.11 & 17.12 Autonomous Threat Response Engine.
Orchestrates policy-controlled autonomous remediation, autonomy levels (0–4),
dry-run simulation, blast-radius calculation, and reversible rollback transactions.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.autonomous_response import (
    AutonomousResponsePolicy,
    ResponsePolicyRule,
    ResponseBlastRadius,
    ResponseRollback
)
from backend.app.models.response_approval import ResponseApproval
from backend.app.models.incident import Incident
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.sensor import Sensor
from backend.app.models.api_key import ApiKey
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("Aegivanta.AutonomousResponse")

VALID_AUTONOMY_LEVELS = [
    "LEVEL_0_OBSERVE",
    "LEVEL_1_RECOMMEND",
    "LEVEL_2_APPROVAL_REQUIRED",
    "LEVEL_3_LIMITED_AUTONOMOUS",
    "LEVEL_4_FULL_AUTONOMOUS"
]

HIGH_IMPACT_ACTIONS = [
    "ISOLATE_ENDPOINT",
    "BLOCK_PRODUCTION_SUBNET",
    "MASS_CONTAINMENT",
    "REVOKE_ROOT_CREDENTIALS"
]


class AutonomousResponseService:
    """Policy-governed autonomous response engine with simulation and rollback safety."""

    @classmethod
    async def get_or_create_tenant_policy(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> AutonomousResponsePolicy:
        """Fetches active autonomous response policy or provisions default Level 2 (Approval Required)."""
        stmt = select(AutonomousResponsePolicy).where(AutonomousResponsePolicy.tenant_id == tenant_id)
        res = await db.execute(stmt)
        policy = res.scalar_one_or_none()

        if not policy:
            policy = AutonomousResponsePolicy(
                tenant_id=tenant_id,
                policy_name="Enterprise Default Autonomous Response Policy",
                description="Default policy mandating human approval for high-impact containment actions.",
                autonomy_level="LEVEL_2_APPROVAL_REQUIRED",
                is_enabled=True,
                min_confidence_threshold=0.85,
                min_risk_threshold=70.0,
                max_blast_radius_assets=3,
                allowed_actions=[
                    "NOTIFY_ADMINISTRATOR",
                    "CREATE_INVESTIGATION",
                    "ENRICH_IOC",
                    "BLOCK_IOC",
                    "QUARANTINE_INDICATOR",
                    "DISABLE_API_KEY",
                    "REVOKE_SESSION",
                    "ISOLATE_ENDPOINT"
                ],
                excluded_assets=[]
            )
            db.add(policy)
            await db.flush()

        return policy

    @classmethod
    async def calculate_blast_radius(
        cls,
        db: AsyncSession,
        tenant_id: str,
        action_type: str,
        target_entity: str
    ) -> ResponseBlastRadius:
        """Analyzes dependency topology to predict operational impact of proposed containment."""
        action_upper = action_type.upper().strip()
        contains_critical = False
        impact = "LOW"
        affected_assets = 1
        affected_users = 0
        affected_sensors = 1

        # Check if target is a known critical asset
        asset_stmt = select(ProtectedAsset).where(
            (ProtectedAsset.ip_address == target_entity) |
            (ProtectedAsset.name == target_entity) |
            (ProtectedAsset.id == target_entity)
        )
        asset_res = await db.execute(asset_stmt)
        asset = asset_res.scalar_one_or_none()

        if asset:
            if str(asset.criticality).upper() in ["CRITICAL", "HIGH"]:
                contains_critical = True
                impact = "CRITICAL" if str(asset.criticality).upper() == "CRITICAL" else "HIGH"
                affected_users = 25

        if action_upper in HIGH_IMPACT_ACTIONS:
            impact = "HIGH" if impact == "LOW" else impact

        record = ResponseBlastRadius(
            action_type=action_upper,
            target_entity=target_entity,
            tenant_id=tenant_id,
            affected_assets_count=affected_assets,
            affected_users_count=affected_users,
            affected_sensors_count=affected_sensors,
            contains_production_critical=contains_critical,
            estimated_business_impact=impact,
            rollback_supported=action_upper in ["BLOCK_IP", "ISOLATE_ENDPOINT", "DISABLE_API_KEY", "BLOCK_IOC"]
        )
        db.add(record)
        await db.flush()
        return record

    @classmethod
    async def simulate_response(
        cls,
        db: AsyncSession,
        tenant_id: str,
        incident_id: str,
        action_type: str,
        target_entity: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a dry-run evaluation of an autonomous response action:
        Returns structured decision, policy match, blast radius, and approval requirement.
        """
        policy = await cls.get_or_create_tenant_policy(db, tenant_id)
        blast_radius = await cls.calculate_blast_radius(db, tenant_id, action_type, target_entity)

        action_norm = action_type.upper().strip()
        is_allowed = policy.is_enabled and (action_norm in (policy.allowed_actions or []))

        # Autonomy Level evaluation
        autonomy = policy.autonomy_level
        requires_approval = True

        if autonomy == "LEVEL_0_OBSERVE":
            is_allowed = False
            requires_approval = True
            explanation = "Tenant is configured in LEVEL_0_OBSERVE mode: All active responses are suppressed."
        elif autonomy == "LEVEL_1_RECOMMEND":
            is_allowed = False
            requires_approval = True
            explanation = "Tenant is configured in LEVEL_1_RECOMMEND mode: Recommendations generated for human review only."
        elif autonomy == "LEVEL_2_APPROVAL_REQUIRED":
            requires_approval = True
            explanation = f"Action '{action_norm}' requires human administrator approval prior to execution."
        elif autonomy == "LEVEL_3_LIMITED_AUTONOMOUS":
            if action_norm in HIGH_IMPACT_ACTIONS or blast_radius.contains_production_critical:
                requires_approval = True
                explanation = f"Action '{action_norm}' affects critical infrastructure; human approval required under LEVEL_3."
            else:
                requires_approval = False
                explanation = f"Action '{action_norm}' qualifies for autonomous execution under LEVEL_3."
        elif autonomy == "LEVEL_4_FULL_AUTONOMOUS":
            requires_approval = False
            explanation = f"Action '{action_norm}' approved for full autonomous execution."
        else:
            explanation = f"Defaulting to human approval required."

        return {
            "tenant_id": tenant_id,
            "incident_id": incident_id,
            "action_type": action_norm,
            "target_entity": target_entity,
            "decision": "ALLOWED" if is_allowed else "DENIED",
            "autonomy_level": autonomy,
            "requires_approval": requires_approval,
            "blast_radius": {
                "affected_assets_count": blast_radius.affected_assets_count,
                "contains_production_critical": blast_radius.contains_production_critical,
                "estimated_business_impact": blast_radius.estimated_business_impact,
                "rollback_supported": blast_radius.rollback_supported
            },
            "explanation": explanation,
            "simulation_timestamp": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    async def execute_response(
        cls,
        db: AsyncSession,
        tenant_id: str,
        incident_id: str,
        action_type: str,
        target_entity: str,
        actor: str = "AUTONOMOUS_ENGINE",
        bypass_approval: bool = False
    ) -> Dict[str, Any]:
        """Validates policy and executes or requests approval for a response action."""
        sim = await cls.simulate_response(
            db=db,
            tenant_id=tenant_id,
            incident_id=incident_id,
            action_type=action_type,
            target_entity=target_entity
        )

        if sim["decision"] != "ALLOWED":
            raise SentinelAIException(
                status_code=403,
                detail=f"Response action '{action_type}' denied by tenant policy: {sim['explanation']}"
            )

        if sim["requires_approval"] and not bypass_approval:
            # Create approval ticket
            approval = ResponseApproval(
                incident_id=incident_id,
                requested_action=action_type.upper(),
                target_entity=target_entity,
                requested_by=actor,
                status="REQUESTED",
                reason=sim["explanation"],
                is_dry_run=False
            )
            db.add(approval)
            await db.flush()

            return {
                "status": "PENDING_APPROVAL",
                "approval_id": approval.id,
                "action_type": action_type.upper(),
                "target_entity": target_entity,
                "message": "Action successfully queued for human administrator approval."
            }

        # Safe Execution Logic
        action_norm = action_type.upper().strip()
        original_state = {"status": "ACTIVE"}
        modified_state = {"status": "CONTAINED"}
        rollback_op = f"RESTORE_{action_norm}"

        if action_norm == "ISOLATE_ENDPOINT":
            sensor_stmt = select(Sensor).where(Sensor.id == target_entity)
            sensor = (await db.execute(sensor_stmt)).scalar_one_or_none()
            if sensor:
                original_state["sensor_status"] = sensor.status
                sensor.status = "ISOLATED"
                modified_state["sensor_status"] = "ISOLATED"

        elif action_norm == "DISABLE_API_KEY":
            key_stmt = select(ApiKey).where(ApiKey.id == target_entity)
            key_rec = (await db.execute(key_stmt)).scalar_one_or_none()
            if key_rec:
                original_state["is_active"] = key_rec.is_active
                key_rec.is_active = False
                modified_state["is_active"] = False

        # Record Rollback Transaction
        action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
        rollback_rec = ResponseRollback(
            action_id=action_id,
            tenant_id=tenant_id,
            action_type=action_norm,
            target_entity=target_entity,
            original_state=original_state,
            modified_state=modified_state,
            rollback_operation=rollback_op,
            rollback_status="PENDING",
            executed_by=actor
        )
        db.add(rollback_rec)
        await db.flush()

        return {
            "status": "EXECUTED",
            "action_id": action_id,
            "action_type": action_norm,
            "target_entity": target_entity,
            "executed_by": actor,
            "rollback_id": rollback_rec.id,
            "executed_at": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    async def rollback_response(
        cls,
        db: AsyncSession,
        tenant_id: str,
        action_id: str,
        actor: str = "ADMINISTRATOR"
    ) -> Dict[str, Any]:
        """Rolls back a previously executed reversible response action."""
        stmt = select(ResponseRollback).where(
            and_(
                ResponseRollback.action_id == action_id,
                ResponseRollback.tenant_id == tenant_id
            )
        )
        res = await db.execute(stmt)
        rollback = res.scalar_one_or_none()

        if not rollback:
            raise SentinelAIException(status_code=404, detail="Rollback record not found for action ID.")

        if rollback.rollback_status == "COMPLETED":
            raise SentinelAIException(status_code=400, detail="Action has already been rolled back.")

        # Execute reverse operation
        if rollback.action_type == "ISOLATE_ENDPOINT":
            sensor_stmt = select(Sensor).where(Sensor.id == rollback.target_entity)
            sensor = (await db.execute(sensor_stmt)).scalar_one_or_none()
            if sensor:
                sensor.status = rollback.original_state.get("sensor_status", "ONLINE")

        elif rollback.action_type == "DISABLE_API_KEY":
            key_stmt = select(ApiKey).where(ApiKey.id == rollback.target_entity)
            key_rec = (await db.execute(key_stmt)).scalar_one_or_none()
            if key_rec:
                key_rec.is_active = rollback.original_state.get("is_active", True)

        rollback.rollback_status = "COMPLETED"
        rollback.completed_at = datetime.now(timezone.utc)
        await db.flush()

        return {
            "status": "ROLLED_BACK",
            "action_id": action_id,
            "action_type": rollback.action_type,
            "target_entity": rollback.target_entity,
            "rolled_back_by": actor,
            "completed_at": rollback.completed_at.isoformat()
        }
