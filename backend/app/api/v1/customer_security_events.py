from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.models.security_policy import CustomerSecurityEvent
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/security/events", tags=["Customer Security Events"])


class SecurityEventListItem(BaseModel):
    id: str
    event_type: str
    severity: str
    action: str
    actor_id: str
    actor_email: Optional[str]
    ip_address: Optional[str]
    details_json: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[SecurityEventListItem], summary="List Customer Security Events")
async def list_security_events(
    limit: int = 50,
    context: TenantContext = Depends(require_tenant_role(TenantRole.SECURITY_ANALYST)),
    db: AsyncSession = Depends(get_db)
):
    """Lists auditable customer security events (MFA enrollments, session revokes, policy changes)."""
    if not context.organization_id:
        return []

    stmt = (
        select(CustomerSecurityEvent)
        .where(CustomerSecurityEvent.organization_id == context.organization_id)
        .order_by(CustomerSecurityEvent.timestamp.desc())
        .limit(min(100, limit))
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())
