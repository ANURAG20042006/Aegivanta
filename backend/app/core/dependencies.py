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


def require_role(allowed_roles: list[str]) -> Callable:
    """Factory dependency for enforcing Role-Based Access Control (RBAC)."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError(
                detail=f"Role '{current_user.role}' is not authorized. Required: {allowed_roles}"
            )
        return current_user
    return role_checker
