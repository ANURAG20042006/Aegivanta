"""
backend/app/api/v1/security_automation_studio.py
================================================
Phase 46 Security Automation Studio (Visual Playbook Builder & SOAR Workflow Canvas) Router.
Exposes:
- Automation Studio Posture Scorecard
- Visual DAG Playbook Management & Publishing
- Playbook Execution Logs & Dry-Run Simulator
- Turnkey Automation Template Catalog
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.playbook_builder_service import PlaybookBuilderService
from backend.app.services.playbook_engine_service import PlaybookEngineService
from backend.app.services.automation_studio_posture_service import AutomationStudioPostureService

router = APIRouter(prefix="/automation-studio", tags=["Phase 46 - Security Automation Studio"])


# ==================== Request Payloads ====================

class CreatePlaybookRequest(BaseModel):
    name: str = Field(..., example="Automated Threat Hunting & Host Containment")
    description: str = Field(..., example="Executes live threat sweep and isolates suspicious processes.")
    trigger_type: str = Field(default="ON_ALERT", example="ON_ALERT")
    canvas_graph_json: Optional[Dict[str, Any]] = None


class SimulatePlaybookRequest(BaseModel):
    playbook_name: str = Field(..., example="Ransomware Containment & Host Isolation")
    trigger_payload: Optional[Dict[str, Any]] = None


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Security Automation Studio Posture Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated automation studio scorecard metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await AutomationStudioPostureService.get_summary(db=db, tenant_id=tenant_id)


@router.get("/playbooks", summary="List Automation Playbooks")
async def list_playbooks(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active playbooks for a tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PlaybookBuilderService.list_playbooks(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/playbooks", summary="Create New Automation Playbook")
async def create_playbook(
    req: CreatePlaybookRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new DAG automation playbook."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PlaybookBuilderService.create_playbook(
        db=db,
        tenant_id=tenant_id,
        name=req.name,
        description=req.description,
        trigger_type=req.trigger_type,
        canvas_graph_json=req.canvas_graph_json
    )


@router.get("/executions", summary="List Playbook Execution Runs")
async def list_executions(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists recent playbook execution runs."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PlaybookEngineService.list_executions(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/simulate", summary="Simulate Playbook Dry-Run Execution")
async def simulate_execution(
    req: SimulatePlaybookRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Performs a dry-run execution simulation through all DAG steps."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PlaybookEngineService.simulate_execution(
        db=db,
        tenant_id=tenant_id,
        playbook_name=req.playbook_name,
        trigger_payload=req.trigger_payload
    )


@router.get("/templates", summary="List Turnkey Playbook Templates")
async def list_templates(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists pre-built turnkey automation templates."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PlaybookBuilderService.list_templates(db=db, tenant_id=tenant_id, limit=limit)
