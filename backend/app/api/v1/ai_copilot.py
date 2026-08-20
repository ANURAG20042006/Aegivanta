from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.services.ai_copilot_service import AICopilotService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/copilot", tags=["AI Security Copilot"])


class CopilotQueryRequest(BaseModel):
    query: str
    incident_id: Optional[str] = None


@router.post("/query", summary="Query AI Security Copilot")
async def query_copilot(
    payload: CopilotQueryRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Processes analyst queries, summarizes incident context, and provides explainable attack paths."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    return await AICopilotService.chat_query(
        db=db,
        tenant_id=context.tenant_id,
        user_query=payload.query,
        incident_id=payload.incident_id
    )


@router.get("/incidents/{incident_id}/explain", summary="Generate Incident AI Explanation & Response Guidance")
async def explain_incident(
    incident_id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates explainable attack path, MITRE mapping, evidence summary, and gated SOAR containment proposals."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    return await AICopilotService.analyze_incident(
        db=db,
        incident_id=incident_id,
        tenant_id=context.tenant_id
    )
