from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.advanced_hunting_service import AdvancedHuntingService

router = APIRouter(prefix="/hunting-workbench", tags=["Threat Hunting Workbench"])


class ExecuteHuntRequest(BaseModel):
    target_entity: str
    query_pattern: str
    limit: Optional[int] = 50


@router.get("/templates", summary="Get Standard Threat Hunting Templates")
async def get_hunt_templates(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns library of parameterized threat hunting query templates."""
    return await AdvancedHuntingService.get_hunt_templates()


@router.post("/execute", summary="Execute Advanced Threat Hunt")
async def execute_hunt(
    payload: ExecuteHuntRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes multi-entity threat hunting query and records execution metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    executed_by = context.user_id or "ANALYST"
    return await AdvancedHuntingService.execute_hunt(
        db=db,
        tenant_id=tenant_id,
        target_entity=payload.target_entity,
        query_pattern=payload.query_pattern,
        limit=payload.limit or 50,
        executed_by=executed_by
    )
