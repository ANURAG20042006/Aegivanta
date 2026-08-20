from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.security_validation_service import SecurityValidationService

router = APIRouter(prefix="/security/validation", tags=["Continuous Defense Validation"])


@router.get("", summary="Get Latest Continuous Security Validation Results")
async def get_latest_validation(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns the most recent security defense validation run and check breakdown."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SecurityValidationService.get_latest_validation(db, tenant_id)


@router.post("/run", summary="Trigger Continuous Defense Validation Run")
async def trigger_validation_run(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes on-demand non-destructive audit of all active security controls."""
    tenant_id = context.tenant_id or "default-tenant"
    run = await SecurityValidationService.run_validation(db, tenant_id, "MANUAL")
    return await SecurityValidationService.get_latest_validation(db, tenant_id)
