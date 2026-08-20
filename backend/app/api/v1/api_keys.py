from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.models.api_key import ApiKey, ApiKeyScope
from backend.app.services.api_key_service import ApiKeyService
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


class CreateApiKeyRequest(BaseModel):
    name: str
    scopes: List[str]
    rate_limit_rpm: Optional[int] = 60
    ip_restrictions: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class ApiKeyCreatedResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    secret_key: str  # Displayed only once upon creation
    scopes: List[str]
    rate_limit_rpm: int
    created_at: datetime


class ApiKeyListItem(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: List[str]
    rate_limit_rpm: int
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime


@router.post("", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED, summary="Create New Customer API Key")
async def create_api_key(
    payload: CreateApiKeyRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.API_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Generates a new secure customer API key. The secret key is only displayed once."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant context required to provision API key.")

    key_record, raw_secret = await ApiKeyService.create_api_key(
        db=db,
        tenant_id=context.tenant_id,
        name=payload.name,
        scopes=payload.scopes,
        user_id=context.user_id,
        rate_limit_rpm=payload.rate_limit_rpm or 60,
        ip_restrictions=payload.ip_restrictions,
        expires_at=payload.expires_at
    )

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"api_key:{key_record.id}",
        action=f"Generated API key '{key_record.name}' with prefix '{key_record.key_prefix}'"
    )

    await db.commit()

    scopes_list = key_record.scopes.get("scopes", []) if isinstance(key_record.scopes, dict) else []
    return ApiKeyCreatedResponse(
        id=key_record.id,
        name=key_record.name,
        key_prefix=key_record.key_prefix,
        secret_key=raw_secret,
        scopes=scopes_list,
        rate_limit_rpm=key_record.rate_limit_rpm,
        created_at=key_record.created_at
    )


@router.get("", response_model=List[ApiKeyListItem], summary="List Tenant API Keys")
async def list_api_keys(
    context: TenantContext = Depends(require_tenant_role(TenantRole.API_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lists all active and revoked API keys for the current tenant. Secrets are never exposed."""
    if not context.tenant_id:
        return []

    stmt = select(ApiKey).where(ApiKey.tenant_id == context.tenant_id).order_by(ApiKey.created_at.desc())
    res = await db.execute(stmt)
    records = res.scalars().all()

    items = []
    for k in records:
        scopes_list = k.scopes.get("scopes", []) if isinstance(k.scopes, dict) else []
        items.append(ApiKeyListItem(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            scopes=scopes_list,
            rate_limit_rpm=k.rate_limit_rpm,
            is_active=k.is_active,
            last_used_at=k.last_used_at,
            created_at=k.created_at
        ))
    return items


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke API Key")
async def revoke_api_key(
    key_id: str,
    context: TenantContext = Depends(require_tenant_role(TenantRole.API_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Revokes an active API key immediately."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    success = await ApiKeyService.revoke_api_key(db, key_id, context.tenant_id)
    if not success:
        raise SentinelAIException(status_code=404, detail="API key not found or not owned by tenant.")

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"api_key:{key_id}",
        action=f"Revoked API key ID '{key_id}'"
    )
    await db.commit()
