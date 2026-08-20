from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.services.security_policy_service import SecurityPolicyService
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/security/policies", tags=["Enterprise Security Policies"])


class SecurityPolicyResponse(BaseModel):
    id: str
    organization_id: str
    require_mfa: bool
    require_sso: bool
    session_timeout_minutes: int
    max_concurrent_sessions: int
    api_key_max_ttl_days: int
    ip_allowlist: Optional[Dict[str, Any]]
    ip_denylist: Optional[Dict[str, Any]]
    password_min_length: int
    require_password_special_char: bool

    class Config:
        from_attributes = True


class UpdateSecurityPolicyRequest(BaseModel):
    require_mfa: Optional[bool] = None
    require_sso: Optional[bool] = None
    session_timeout_minutes: Optional[int] = None
    max_concurrent_sessions: Optional[int] = None
    api_key_max_ttl_days: Optional[int] = None
    ip_allowlist: Optional[List[str]] = None
    ip_denylist: Optional[List[str]] = None
    password_min_length: Optional[int] = None
    require_password_special_char: Optional[bool] = None


@router.get("", response_model=SecurityPolicyResponse, summary="Get Active Security Policy")
async def get_security_policy(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Fetches organization security baseline, MFA/SSO requirements, and IP restrictions."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    policy = await SecurityPolicyService.get_or_create_policy(db, context.organization_id)
    return policy


@router.put("", response_model=SecurityPolicyResponse, summary="Update Organization Security Policies")
async def update_security_policy(
    payload: UpdateSecurityPolicyRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Updates security guardrails (enforcing MFA/SSO, session limits, IP whitelists)."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    policy = await SecurityPolicyService.get_or_create_policy(db, context.organization_id)

    if payload.require_mfa is not None:
        policy.require_mfa = payload.require_mfa
    if payload.require_sso is not None:
        policy.require_sso = payload.require_sso
    if payload.session_timeout_minutes is not None:
        policy.session_timeout_minutes = payload.session_timeout_minutes
    if payload.max_concurrent_sessions is not None:
        policy.max_concurrent_sessions = payload.max_concurrent_sessions
    if payload.api_key_max_ttl_days is not None:
        policy.api_key_max_ttl_days = payload.api_key_max_ttl_days
    if payload.ip_allowlist is not None:
        policy.ip_allowlist = {"ips": payload.ip_allowlist}
    if payload.ip_denylist is not None:
        policy.ip_denylist = {"ips": payload.ip_denylist}
    if payload.password_min_length is not None:
        policy.password_min_length = payload.password_min_length
    if payload.require_password_special_char is not None:
        policy.require_password_special_char = payload.require_password_special_char

    # Immutable Audit Log
    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"org:{context.organization_id}:policy",
        action="Updated enterprise security policy baseline"
    )

    await db.commit()
    await db.refresh(policy)
    return policy
