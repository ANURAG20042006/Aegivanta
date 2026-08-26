"""
backend/app/api/v1/security_scorecard.py
========================================
Phase 26.14 Enterprise Security Scorecard API Endpoint.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.enterprise_security_scorecard_service import EnterpriseSecurityScorecardService

router = APIRouter(prefix="/security", tags=["Enterprise Security Scorecard"])


@router.get("/scorecard", summary="Get Enterprise Security Scorecard")
async def get_security_scorecard(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns consolidated 0–100 customer security index synthesized from
    identity, detection quality, endpoint posture, continuous validation, and SRE health.
    """
    tenant_id = get_enforced_tenant_id(context)
    return await EnterpriseSecurityScorecardService.get_enterprise_scorecard(db, tenant_id)
