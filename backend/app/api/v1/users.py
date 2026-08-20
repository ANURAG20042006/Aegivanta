from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.user import UserResponse, UserCreate, UserUpdate
from backend.app.security import hash_password
from backend.app.core.exceptions import NotFoundError, AegivantaException, SentinelAIException
from backend.app.core.dependencies import require_role

router = APIRouter(prefix="/users", tags=["Users Management"])


@router.get("", response_model=List[UserResponse], summary="List All Users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves all registered system users."""
    query = select(User).order_by(User.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse, summary="Get User Details by ID")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Fetches details for a specific user ID."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError(resource_name="User", resource_id=user_id)
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create User Account (Admin Only)")
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """Creates a new user profile with specified role."""
    query = select(User).where((User.username == payload.username) | (User.email == payload.email))
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise SentinelAIException(status_code=400, detail="Username or email already exists.")

    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=payload.is_active
    )
    db.add(new_user)
    await db.flush()

    audit = AuditLog(
        user_id=admin_user.id,
        action="ADMIN_CREATED_USER",
        resource="USERS",
        status="SUCCESS",
        details={"created_user_id": new_user.id, "target_role": new_user.role}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse, summary="Update User Details (Admin Only)")
async def update_user(
    user_id: str,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """Updates user information such as email, role, or active status."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError(resource_name="User", resource_id=user_id)

    if payload.email is not None:
        user.email = payload.email
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    audit = AuditLog(
        user_id=admin_user.id,
        action="ADMIN_UPDATED_USER",
        resource="USERS",
        status="SUCCESS",
        details={"target_user_id": user.id}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete User Account (Admin Only)")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """Deletes a user account from the system."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError(resource_name="User", resource_id=user_id)

    await db.delete(user)
    audit = AuditLog(
        user_id=admin_user.id,
        action="ADMIN_DELETED_USER",
        resource="USERS",
        status="SUCCESS",
        details={"deleted_user_id": user_id}
    )
    db.add(audit)
    await db.commit()
