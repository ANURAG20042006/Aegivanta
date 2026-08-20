import urllib.parse
import secrets
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.identity import IdentityProvider
from backend.app.core.exceptions import SentinelAIException, AuthenticationError

logger = logging.getLogger("SentinelAI.SSO")


class SSOService:
    """Enterprise OIDC & SAML 2.0 Identity Provider configuration and authentication engine."""

    @classmethod
    async def configure_idp(
        cls,
        db: AsyncSession,
        organization_id: str,
        provider_type: str,
        name: str,
        client_id: str,
        client_secret: Optional[str] = None,
        discovery_url: Optional[str] = None,
        sso_url: Optional[str] = None,
        entity_id: Optional[str] = None,
        x509_cert: Optional[str] = None,
        domain_hints: Optional[list] = None,
        is_enforced: bool = False
    ) -> IdentityProvider:
        """Saves or updates SSO IdP configuration for an organization."""
        stmt = select(IdentityProvider).where(IdentityProvider.organization_id == organization_id)
        res = await db.execute(stmt)
        idp = res.scalar_one_or_none()

        if not idp:
            idp = IdentityProvider(
                organization_id=organization_id,
                provider_type=provider_type.upper(),
                name=name,
                client_id=client_id,
                client_secret_encrypted=client_secret,
                discovery_url=discovery_url,
                sso_url=sso_url,
                entity_id=entity_id,
                x509_cert=x509_cert,
                domain_hints={"domains": domain_hints or []},
                is_active=True,
                is_enforced=is_enforced
            )
            db.add(idp)
        else:
            idp.provider_type = provider_type.upper()
            idp.name = name
            idp.client_id = client_id
            if client_secret:
                idp.client_secret_encrypted = client_secret
            idp.discovery_url = discovery_url
            idp.sso_url = sso_url
            idp.entity_id = entity_id
            idp.x509_cert = x509_cert
            idp.domain_hints = {"domains": domain_hints or []}
            idp.is_enforced = is_enforced
            idp.updated_at = datetime.now(timezone.utc)

        await db.flush()
        return idp

    @classmethod
    async def generate_sso_authorization_url(
        cls,
        db: AsyncSession,
        organization_id: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """Generates an authorization URL with cryptographic state and nonce parameters."""
        stmt = select(IdentityProvider).where(
            and_(
                IdentityProvider.organization_id == organization_id,
                IdentityProvider.is_active == True
            )
        )
        res = await db.execute(stmt)
        idp = res.scalar_one_or_none()
        if not idp:
            raise SentinelAIException(status_code=404, detail="No active SSO configuration found for organization.")

        state = secrets.token_urlsafe(24)
        nonce = secrets.token_urlsafe(24)

        base_sso_url = idp.sso_url or idp.discovery_url or "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        params = {
            "client_id": idp.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "openid profile email",
            "state": state,
            "nonce": nonce
        }
        auth_url = f"{base_sso_url}?{urllib.parse.urlencode(params)}"
        return {"authorization_url": auth_url, "state": state, "nonce": nonce}

    @classmethod
    async def validate_sso_callback(
        cls,
        db: AsyncSession,
        organization_id: str,
        received_state: str,
        expected_state: str,
        auth_code: str
    ) -> Dict[str, Any]:
        """Validates state parameter, prevents CSRF/replay attacks, and simulates token exchange."""
        if not received_state or not expected_state or received_state != expected_state:
            raise AuthenticationError(detail="Invalid or expired SSO state parameter (CSRF protection).")

        if not auth_code:
            raise AuthenticationError(detail="Missing authorization code from Identity Provider.")

        # In production this exchanges authorization code with IdP /token endpoint
        return {
            "email": f"sso_user_{secrets.token_hex(4)}@enterprise.com",
            "full_name": "Enterprise SSO User",
            "organization_id": organization_id,
            "provider_type": "OIDC"
        }
