import hashlib
import secrets
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.scim import SCIMConfiguration, SCIMProvisioningEvent
from backend.app.models.user import User
from backend.app.models.tenant import TenantMembership, TenantRole
from backend.app.security import hash_password
from backend.app.core.exceptions import SentinelAIException, AuthenticationError

logger = logging.getLogger("SentinelAI.SCIM")


class SCIMService:
    """RFC 7644 SCIM 2.0 Identity Provisioning Service."""

    @classmethod
    def _hash_token(cls, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @classmethod
    async def configure_scim(
        cls,
        db: AsyncSession,
        organization_id: str,
        default_role: str = "SECURITY_ANALYST"
    ) -> Tuple[SCIMConfiguration, str]:
        """Provisions a SCIM endpoint configuration and generates bearer token."""
        raw_token = f"scim_{secrets.token_hex(32)}"
        token_hash = cls._hash_token(raw_token)

        stmt = select(SCIMConfiguration).where(SCIMConfiguration.organization_id == organization_id)
        res = await db.execute(stmt)
        config = res.scalar_one_or_none()

        if not config:
            config = SCIMConfiguration(
                organization_id=organization_id,
                bearer_token_hash=token_hash,
                default_role=default_role,
                is_active=True
            )
            db.add(config)
        else:
            config.bearer_token_hash = token_hash
            config.default_role = default_role
            config.is_active = True
            config.updated_at = datetime.now(timezone.utc)

        await db.flush()
        return config, raw_token

    @classmethod
    async def authenticate_scim_request(
        cls,
        db: AsyncSession,
        bearer_token: str
    ) -> Optional[SCIMConfiguration]:
        """Validates SCIM bearer token."""
        if not bearer_token:
            return None
        token_hash = cls._hash_token(bearer_token.strip())

        stmt = select(SCIMConfiguration).where(
            and_(
                SCIMConfiguration.bearer_token_hash == token_hash,
                SCIMConfiguration.is_active == True
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @classmethod
    async def provision_user(
        cls,
        db: AsyncSession,
        organization_id: str,
        scim_user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handles SCIM POST /Users to create or update user profile."""
        username = scim_user_data.get("userName")
        emails = scim_user_data.get("emails", [])
        email = emails[0].get("value") if emails else f"{username}@domain.internal"
        name_obj = scim_user_data.get("name", {})
        display_name = scim_user_data.get("displayName") or f"{name_obj.get('givenName', '')} {name_obj.get('familyName', '')}".strip() or username

        # Check if user already exists
        stmt = select(User).where((User.username == username) | (User.email == email))
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user:
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(secrets.token_urlsafe(32)),  # Random password for SCIM users
                full_name=display_name,
                role="analyst",
                is_active=scim_user_data.get("active", True)
            )
            db.add(user)
            await db.flush()

        # Add tenant membership
        stmt_mem = select(TenantMembership).where(
            and_(
                TenantMembership.organization_id == organization_id,
                TenantMembership.user_id == user.id
            )
        )
        res_mem = await db.execute(stmt_mem)
        if not res_mem.scalar_one_or_none():
            mem = TenantMembership(
                user_id=user.id,
                organization_id=organization_id,
                role=TenantRole.SECURITY_ANALYST.value,
                status="ACTIVE"
            )
            db.add(mem)

        # Audit Event
        event = SCIMProvisioningEvent(
            organization_id=organization_id,
            action="CREATE_USER",
            external_id=scim_user_data.get("externalId"),
            user_id=user.id,
            details_json={"username": user.username, "email": user.email}
        )
        db.add(event)
        await db.flush()

        created_str = user.created_at.isoformat() if user.created_at else datetime.now(timezone.utc).isoformat()

        return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": user.id,
            "userName": user.username,
            "name": {"formatted": user.full_name},
            "emails": [{"value": user.email, "primary": True}],
            "active": user.is_active,
            "meta": {
                "resourceType": "User",
                "created": created_str
            }
        }


    @classmethod
    async def deactivate_user(
        cls,
        db: AsyncSession,
        organization_id: str,
        user_id: str
    ) -> bool:
        """Deactivates a user account via SCIM delete/disable."""
        stmt = select(User).where(User.id == user_id)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            return False

        user.is_active = False

        event = SCIMProvisioningEvent(
            organization_id=organization_id,
            action="DEACTIVATE_USER",
            user_id=user.id,
            details_json={"action": "deactivated"}
        )
        db.add(event)
        await db.flush()
        return True
