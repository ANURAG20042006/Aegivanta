from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.models.integration import CustomerIntegration
from backend.app.services.integration_service import IntegrationService
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/integrations", tags=["Integrations"])


class CreateIntegrationRequest(BaseModel):
    integration_type: str  # SIEM, SLACK, WEBHOOK, EDR, JIRA
    name: str
    config: Dict[str, Any]
    secret: Optional[str] = None


class IntegrationResponse(BaseModel):
    id: str
    organization_id: str
    integration_type: str
    name: str
    status: str
    config_json: Optional[Dict[str, Any]]
    last_sync_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED, summary="Create External Integration Connector")
async def create_integration(
    payload: CreateIntegrationRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Registers an external security tool connector (SIEM, Slack, Webhook, EDR, Jira)."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    integ = await IntegrationService.create_integration(
        db=db,
        organization_id=context.organization_id,
        integration_type=payload.integration_type,
        name=payload.name,
        config=payload.config,
        secret=payload.secret,
        tenant_id=context.tenant_id
    )

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"integration:{integ.id}",
        action=f"Configured {integ.integration_type} integration '{integ.name}'"
    )

    await db.commit()
    return integ


@router.get("", response_model=List[IntegrationResponse], summary="List Configured Integrations")
async def list_integrations(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists all active integrations for the customer organization."""
    if not context.organization_id:
        return []

    stmt = select(CustomerIntegration).where(CustomerIntegration.organization_id == context.organization_id)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/{integration_id}/test", summary="Test Integration Connector Dispatch")
async def test_integration_connector(
    integration_id: str,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Triggers an automated connectivity test dispatch to the external integration endpoint."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    result = await IntegrationService.test_integration(db, integration_id, context.organization_id)
    await db.commit()
    return result


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Integration Connector")
async def delete_integration(
    integration_id: str,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Removes an integration connector."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    stmt = select(CustomerIntegration).where(
        and_(
            CustomerIntegration.id == integration_id,
            CustomerIntegration.organization_id == context.organization_id
        )
    )
    res = await db.execute(stmt)
    integ = res.scalar_one_or_none()
    if not integ:
        raise SentinelAIException(status_code=404, detail="Integration not found.")

    await db.delete(integ)
    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"integration:{integration_id}",
        action=f"Deleted integration '{integ.name}'"
    )
    await db.commit()
