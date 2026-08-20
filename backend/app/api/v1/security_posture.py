from typing import Dict, Any, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.security_posture_service import SecurityPostureService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/security/posture", tags=["Security Posture Management"])


@router.get("", summary="Get Organization Security Posture Score & Breakdown")
async def get_security_posture(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes an explainable 0–100 security posture score across Identity,
    API security, Sensor fleet health, Integration reliability, and Compliance.
    """
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    posture_data = await SecurityPostureService.calculate_posture(db, context.organization_id)
    return posture_data
