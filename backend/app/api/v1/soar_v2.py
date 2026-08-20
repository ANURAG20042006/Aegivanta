from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.soar_orchestrator_v2 import SOAROrchestratorV2
from backend.app.services.soar_connector_service import SOARConnectorService
from backend.app.models.soar_v2 import DeclarativePlaybook, SOARExecutionSession, SOARKillSwitch
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/soar", tags=["Autonomous SOC & SOAR 2.0"])


class CreatePlaybookRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "CONTAINMENT"
    trigger_type: Optional[str] = "ALERT_CRITICAL"
    trigger_conditions: Optional[Dict[str, Any]] = None
    steps: List[Dict[str, Any]]
    requires_human_approval: Optional[bool] = False
    timeout_seconds: Optional[int] = 300


class ExecutePlaybookRequest(BaseModel):
    incident_id: Optional[str] = None
    alert_id: Optional[str] = None


class EvaluateDecisionRequest(BaseModel):
    severity: str
    confidence: float
    threat_score: float
    asset_criticality: str
    kill_chain_stage: Optional[str] = "EXPLOITATION"


class ToggleKillSwitchRequest(BaseModel):
    is_active: bool
    reason: Optional[str] = None


@router.get("/playbooks", summary="List Declarative Playbooks")
async def list_playbooks(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all declarative SOAR playbooks configured for the tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    stmt = select(DeclarativePlaybook).where(DeclarativePlaybook.tenant_id == tenant_id)
    playbooks = list((await db.execute(stmt)).scalars().all())

    if not playbooks:
        # Seed standard containment playbook
        sample = DeclarativePlaybook(
            tenant_id=tenant_id,
            name="C2 Intrusion Automated Rapid Containment",
            description="Isolates infected endpoint and blocks outbound C2 destination IP.",
            category="CONTAINMENT",
            version=1,
            status="PUBLISHED",
            trigger_type="ALERT_CRITICAL",
            steps=[
                {"step_id": "step-1", "action_type": "BLOCK_IP", "target_entity": "198.51.100.22", "requires_approval": False},
                {"step_id": "step-2", "action_type": "CONTAIN_ENDPOINT", "target_entity": "HOST-FIN-01", "requires_approval": True}
            ],
            requires_human_approval=False
        )
        db.add(sample)
        await db.flush()
        playbooks = [sample]

    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "version": p.version,
            "status": p.status,
            "trigger_type": p.trigger_type,
            "steps_count": len(p.steps or []),
            "steps": p.steps,
            "requires_human_approval": p.requires_human_approval,
            "is_enabled": p.is_enabled
        }
        for p in playbooks
    ]


@router.post("/playbooks", summary="Create Declarative Playbook")
async def create_playbook(
    payload: CreatePlaybookRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Creates and validates a new declarative SOAR playbook."""
    tenant_id = context.tenant_id or "default-tenant"
    valid, err = SOAROrchestratorV2.validate_playbook_definition(payload.steps)
    if not valid:
        raise SentinelAIException(status_code=400, detail=err)

    playbook = DeclarativePlaybook(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        category=payload.category or "CONTAINMENT",
        trigger_type=payload.trigger_type or "ALERT_CRITICAL",
        trigger_conditions=payload.trigger_conditions or {},
        steps=payload.steps,
        requires_human_approval=payload.requires_human_approval or False,
        timeout_seconds=payload.timeout_seconds or 300,
        created_by=context.user_id or "ADMIN"
    )
    db.add(playbook)
    await db.flush()

    return {"status": "CREATED", "playbook_id": playbook.id, "name": playbook.name}


@router.post("/playbooks/{id}/execute", summary="Execute Playbook")
async def execute_playbook(
    id: str,
    payload: ExecutePlaybookRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes a SOAR playbook in active containment mode."""
    tenant_id = context.tenant_id or "default-tenant"
    session = await SOAROrchestratorV2.execute_playbook_session(
        db=db,
        tenant_id=tenant_id,
        playbook_id=id,
        incident_id=payload.incident_id,
        alert_id=payload.alert_id,
        is_dry_run=False,
        triggered_by=context.user_id or "ANALYST"
    )
    return {
        "execution_id": session.id,
        "status": session.status,
        "total_steps": session.total_steps,
        "step_results": session.step_results
    }


@router.post("/playbooks/{id}/dry-run", summary="Dry-Run Playbook Simulation")
async def dry_run_playbook(
    id: str,
    payload: ExecutePlaybookRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Simulates playbook execution without modifying active infrastructure state."""
    tenant_id = context.tenant_id or "default-tenant"
    session = await SOAROrchestratorV2.execute_playbook_session(
        db=db,
        tenant_id=tenant_id,
        playbook_id=id,
        incident_id=payload.incident_id,
        alert_id=payload.alert_id,
        is_dry_run=True,
        triggered_by=context.user_id or "ANALYST"
    )
    return {
        "execution_id": session.id,
        "status": session.status,
        "is_dry_run": True,
        "step_results": session.step_results
    }


@router.get("/executions", summary="List Execution Sessions")
async def list_executions(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists past SOAR execution sessions."""
    tenant_id = context.tenant_id or "default-tenant"
    stmt = (
        select(SOARExecutionSession)
        .where(SOARExecutionSession.tenant_id == tenant_id)
        .order_by(desc(SOARExecutionSession.started_at))
        .limit(30)
    )
    sessions = list((await db.execute(stmt)).scalars().all())
    return [
        {
            "id": s.id,
            "playbook_id": s.playbook_id,
            "status": s.status,
            "is_dry_run": s.is_dry_run,
            "total_steps": s.total_steps,
            "step_results": s.step_results,
            "triggered_by": s.triggered_by,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        }
        for s in sessions
    ]


@router.post("/decision/evaluate", summary="Evaluate Autonomous Containment Decision")
async def evaluate_decision(
    payload: EvaluateDecisionRequest,
    context: TenantContext = Depends(resolve_tenant_context)
):
    """Evaluates multi-factor containment risk and recommends autonomous vs human action."""
    return SOAROrchestratorV2.evaluate_autonomous_decision(
        severity=payload.severity,
        confidence=payload.confidence,
        threat_score=payload.threat_score,
        asset_criticality=payload.asset_criticality,
        kill_chain_stage=payload.kill_chain_stage or "EXPLOITATION"
    )


@router.get("/kill-switch", summary="Get Emergency Kill Switch Status")
async def get_kill_switch_status(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns the current state of the SOAR emergency containment kill switch."""
    tenant_id = context.tenant_id or "default-tenant"
    is_active = await SOAROrchestratorV2.is_kill_switch_active(db, tenant_id)
    return {"is_active": is_active, "tenant_id": tenant_id}


@router.post("/kill-switch", summary="Toggle Emergency Kill Switch")
async def toggle_kill_switch(
    payload: ToggleKillSwitchRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Activates or deactivates the emergency containment kill switch."""
    tenant_id = context.tenant_id or "default-tenant"
    ks = await SOAROrchestratorV2.toggle_kill_switch(
        db=db,
        tenant_id=tenant_id,
        active=payload.is_active,
        activated_by=context.user_id or "ADMIN",
        reason=payload.reason
    )
    return {"status": "UPDATED", "is_active": ks.is_active}


@router.get("/connectors", summary="List SOAR Connectors")
async def list_connectors(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all registered SOAR security connectors and their health status."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SOARConnectorService.list_connectors(db, tenant_id)


@router.post("/connectors/{id}/health-check", summary="Test Connector Health")
async def check_connector_health(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Runs latency ping and connectivity verification for a SOAR connector."""
    return await SOARConnectorService.test_connector_health(db, id)
