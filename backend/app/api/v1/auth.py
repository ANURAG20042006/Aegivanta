from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.auth import RegisterRequest, Token
from backend.app.schemas.user import UserResponse
from backend.app.security import verify_password, hash_password, create_access_token
from backend.app.core.exceptions import AuthenticationError, SentinelAIException
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="Authenticate User & Obtain JWT Token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticates username and password credentials, returning a signed JWT access token."""
    username = form_data.username
    password = form_data.password

    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        audit = AuditLog(
            action="USER_LOGIN_FAILED",
            resource="AUTH",
            status="FAILURE",
            details={"username": username}
        )
        db.add(audit)
        await db.commit()
        raise AuthenticationError(detail="Invalid username or password.")

    if not user.is_active:
        raise AuthenticationError(detail="User account is deactivated.")

    access_token = create_access_token(subject=user.id, role=user.role)

    audit = AuditLog(
        user_id=user.id,
        action="USER_LOGIN_SUCCESS",
        resource="AUTH",
        status="SUCCESS",
        details={"role": user.role}
    )
    db.add(audit)
    await db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=480,
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register New User")
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Registers a new system user profile."""
    query = select(User).where((User.username == payload.username) | (User.email == payload.email))
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise SentinelAIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered."
        )

    requested_role = (payload.role or "viewer").strip().lower()
    if requested_role in ["admin", "administrator", "root", "analyst", "soc_analyst", "security_analyst"]:
        raise SentinelAIException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration cannot provision privileged accounts (Admin or Analyst). Privileged accounts must be created by an administrator."
        )

    # Public self-registration is strictly restricted to Viewer role
    assigned_role = "viewer"

    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=assigned_role
    )
    db.add(new_user)
    await db.flush()

    audit = AuditLog(
        user_id=new_user.id,
        action="USER_REGISTERED",
        resource="USERS",
        status="SUCCESS",
        details={"username": new_user.username, "role": new_user.role}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponse, summary="Get Current Authenticated User Profile")
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile details of currently authenticated JWT user."""
    return current_user
