from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.compliance_service import ComplianceService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/compliance", tags=["Governance & Compliance"])


@router.get("/posture", summary="Get Enterprise Regulatory Compliance Posture")
async def get_compliance_posture(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates control readiness across SOC 2, ISO 27001, GDPR, NIST CSF, and CIS Controls."""
    org_id = context.organization_id or context.tenant_id
    if not org_id:
        raise SentinelAIException(status_code=400, detail="Active organization or tenant required.")

    return await ComplianceService.get_compliance_posture(db, org_id)
