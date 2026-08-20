import logging
import ipaddress
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.security_policy import SecurityPolicy, CustomerSecurityEvent
from backend.app.core.exceptions import PermissionDeniedError

logger = logging.getLogger("SentinelAI.Policy")


class SecurityPolicyService:
    """Evaluates and enforces enterprise security policies for organizations."""

    @classmethod
    async def get_or_create_policy(
        cls,
        db: AsyncSession,
        organization_id: str
    ) -> SecurityPolicy:
        """Retrieves active security policy or creates sensible default."""
        stmt = select(SecurityPolicy).where(SecurityPolicy.organization_id == organization_id)
        res = await db.execute(stmt)
        policy = res.scalar_one_or_none()

        if not policy:
            policy = SecurityPolicy(
                organization_id=organization_id,
                require_mfa=False,
                require_sso=False,
                session_timeout_minutes=480,
                max_concurrent_sessions=5,
                api_key_max_ttl_days=90,
                password_min_length=12,
                require_password_special_char=True
            )
            db.add(policy)
            await db.flush()

        return policy

    @classmethod
    async def evaluate_login_policy(
        cls,
        db: AsyncSession,
        organization_id: str,
        client_ip: str,
        is_mfa_authenticated: bool = False,
        is_sso_authenticated: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluates incoming login against organization security policies.
        Returns (is_permitted, error_reason).
        """
        policy = await cls.get_or_create_policy(db, organization_id)

        # 1. IP Denylist check
        if policy.ip_denylist and client_ip:
            denied_ips = policy.ip_denylist.get("ips", [])
            for d in denied_ips:
                try:
                    if ipaddress.ip_address(client_ip) in ipaddress.ip_network(d, strict=False):
                        return False, f"Access blocked: IP address '{client_ip}' is in organization denylist."
                except Exception:
                    pass

        # 2. IP Allowlist check (if configured)
        if policy.ip_allowlist and client_ip:
            allowed_ips = policy.ip_allowlist.get("ips", [])
            if allowed_ips:
                matched = False
                for a in allowed_ips:
                    try:
                        if ipaddress.ip_address(client_ip) in ipaddress.ip_network(a, strict=False):
                            matched = True
                            break
                    except Exception:
                        pass
                if not matched:
                    return False, f"Access blocked: IP '{client_ip}' not in organization allowlist."

        # 3. Enforced SSO check
        if policy.require_sso and not is_sso_authenticated:
            return False, "Organization requires all users to authenticate via Enterprise SSO."

        # 4. Enforced MFA check
        if policy.require_mfa and not is_mfa_authenticated:
            return False, "Organization requires Multi-Factor Authentication (MFA)."

        return True, None

    @classmethod
    async def record_security_event(
        cls,
        db: AsyncSession,
        organization_id: str,
        actor_id: str,
        event_type: str,
        action: str,
        severity: str = "INFO",
        ip_address: Optional[str] = None,
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> CustomerSecurityEvent:
        """Records a customer-facing security event."""
        event = CustomerSecurityEvent(
            organization_id=organization_id,
            tenant_id=tenant_id,
            actor_id=actor_id,
            event_type=event_type,
            severity=severity,
            action=action,
            ip_address=ip_address,
            details_json=details or {},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(event)
        await db.flush()
        return event
