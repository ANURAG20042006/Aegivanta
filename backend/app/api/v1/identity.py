from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.user import User
from backend.app.models.tenant import TenantRole
from backend.app.services.identity_service import IdentityService
from backend.app.services.sso_service import SSOService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/identity", tags=["Enterprise Identity, MFA & SSO"])


class MFASetupResponse(BaseModel):
    secret: str
    recovery_codes: List[str]
    otpauth_uri: str


class MFAVerifyRequest(BaseModel):
    code: str


class SessionListItem(BaseModel):
    id: str
    ip_address: str
    user_agent: str
    device_fingerprint: Optional[str]
    is_suspicious: bool
    last_activity_at: datetime
    expires_at: datetime


class SSOConfigRequest(BaseModel):
    provider_type: str  # OIDC, SAML
    name: str
    client_id: str
    client_secret: Optional[str] = None
    discovery_url: Optional[str] = None
    sso_url: Optional[str] = None
    entity_id: Optional[str] = None
    x509_cert: Optional[str] = None
    domain_hints: Optional[List[str]] = None
    is_enforced: Optional[bool] = False


class SSOLoginUrlRequest(BaseModel):
    redirect_uri: str


@router.post("/mfa/setup", response_model=MFASetupResponse, summary="Initiate TOTP MFA Enrollment")
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generates an RFC 6238 TOTP secret, QR code URI, and single-use emergency recovery codes."""
    secret, recovery_codes, otpauth_uri = await IdentityService.enroll_mfa(db, current_user.id)
    await db.commit()
    return MFASetupResponse(
        secret=secret,
        recovery_codes=recovery_codes,
        otpauth_uri=otpauth_uri
    )


@router.post("/mfa/verify", summary="Verify and Activate TOTP MFA")
async def verify_mfa(
    payload: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verifies a 6-digit TOTP code and marks MFA as fully activated."""
    success = await IdentityService.verify_and_activate_mfa(db, current_user.id, payload.code)
    if not success:
        raise SentinelAIException(status_code=400, detail="Invalid TOTP verification code.")
    await db.commit()
    return {"status": "SUCCESS", "message": "MFA has been successfully activated for your account."}


@router.get("/sessions", response_model=List[SessionListItem], summary="List Active User Sessions")
async def list_active_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all active login sessions, device fingerprints, and suspicious location alerts."""
    sessions = await IdentityService.list_active_sessions(db, current_user.id)
    return [
        SessionListItem(
            id=s.id,
            ip_address=s.ip_address,
            user_agent=s.user_agent,
            device_fingerprint=s.device_fingerprint,
            is_suspicious=s.is_suspicious,
            last_activity_at=s.last_activity_at,
            expires_at=s.expires_at
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke Session")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Terminates an active session immediately."""
    success = await IdentityService.revoke_session(db, session_id, current_user.id)
    if not success:
        raise SentinelAIException(status_code=404, detail="Session not found.")
    await db.commit()


@router.post("/sso/config", summary="Configure Enterprise SSO (OIDC / SAML 2.0)")
async def configure_sso(
    payload: SSOConfigRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Sets up an enterprise Identity Provider (Okta, Azure AD, OneLogin, Google Workspace)."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    idp = await SSOService.configure_idp(
        db=db,
        organization_id=context.organization_id,
        provider_type=payload.provider_type,
        name=payload.name,
        client_id=payload.client_id,
        client_secret=payload.client_secret,
        discovery_url=payload.discovery_url,
        sso_url=payload.sso_url,
        entity_id=payload.entity_id,
        x509_cert=payload.x509_cert,
        domain_hints=payload.domain_hints,
        is_enforced=payload.is_enforced or False
    )
    await db.commit()
    return {"status": "SUCCESS", "idp_id": idp.id, "name": idp.name, "provider_type": idp.provider_type}


@router.post("/sso/login-url", summary="Generate SSO Authorization URL")
async def get_sso_login_url(
    payload: SSOLoginUrlRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates an SSO authorization redirect URL with anti-CSRF state and nonce parameters."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    result = await SSOService.generate_sso_authorization_url(
        db=db,
        organization_id=context.organization_id,
        redirect_uri=payload.redirect_uri
    )
    return result
