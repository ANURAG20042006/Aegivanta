from typing import AsyncGenerator, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.security import decode_access_token
from backend.app.models.user import User
from backend.app.core.exceptions import AuthenticationError, PermissionDeniedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to retrieve current authenticated user from JWT bearer token."""
    payload = decode_access_token(token)
    user_id: str = payload.get("sub", "")
    if not user_id:
        raise AuthenticationError(detail="Invalid token payload.")

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError(detail="User account associated with token no longer exists.")
    if not user.is_active:
        raise AuthenticationError(detail="User account is deactivated.")

    return user


# Canonical internal RBAC roles
CANONICAL_ROLES = {"admin", "analyst", "viewer"}

# Role alias dictionary for backward compatibility
ROLE_ALIASES = {
    "admin": "admin",
    "administrator": "admin",
    "root": "admin",
    "analyst": "analyst",
    "soc_analyst": "analyst",
    "security_analyst": "analyst",
    "viewer": "viewer",
    "read_only": "viewer",
    "guest": "viewer",
    "auditor": "viewer"
}


def normalize_role(role: str) -> str:
    """
    Normalizes a role string into its canonical representation.
    Returns 'unknown' for unrecognized or unmapped roles (fail-closed).
    """
    clean_role = (role or "").strip().lower()
    return ROLE_ALIASES.get(clean_role, "unknown")


def require_role(allowed_roles: list[str]) -> Callable:
    """
    Factory dependency for enforcing Role-Based Access Control (RBAC).
    Normalizes both required and user roles to canonical representations.
    Fails closed if the user role is unrecognized or not permitted.
    """
    canonical_allowed = {normalize_role(r) for r in allowed_roles}
    canonical_allowed.discard("unknown")

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_canonical = normalize_role(current_user.role)
        if user_role_canonical not in canonical_allowed:
            raise PermissionDeniedError(
                detail=f"User role '{current_user.role}' is not authorized to access this resource. Required: {allowed_roles}"
            )
        return current_user

    return role_checker
