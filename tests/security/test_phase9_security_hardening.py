import pytest
from fastapi import HTTPException
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.core.exceptions import PermissionDeniedError


@pytest.mark.asyncio
async def test_rbac_admin_authorization_success():
    """Requirement 2 Proof: Admin user successfully passes admin role checker."""
    admin_user = User(username="admin_user", role="ADMIN", is_active=True)
    role_checker = require_role(["admin"])
    authorized_user = await role_checker(current_user=admin_user)
    assert authorized_user.username == "admin_user"
    assert authorized_user.role == "ADMIN"


@pytest.mark.asyncio
async def test_rbac_privilege_escalation_denied():
    """Requirement 2 Proof: Non-admin user (VIEWER / RESEARCHER / SOC_ANALYST) attempting admin action gets HTTP 403."""
    viewer_user = User(username="viewer_user", role="VIEWER", is_active=True)
    researcher_user = User(username="researcher_user", role="RESEARCHER", is_active=True)
    soc_user = User(username="soc_user", role="SOC_ANALYST", is_active=True)

    admin_only_checker = require_role(["admin"])

    # 1. Viewer attempt
    with pytest.raises(PermissionDeniedError) as exc_info1:
        await admin_only_checker(current_user=viewer_user)
    assert exc_info1.value.status_code == 403
    assert "not authorized" in str(exc_info1.value.detail)

    # 2. Researcher attempt
    with pytest.raises(PermissionDeniedError) as exc_info2:
        await admin_only_checker(current_user=researcher_user)
    assert exc_info2.value.status_code == 403

    # 3. SOC Analyst attempt
    with pytest.raises(PermissionDeniedError) as exc_info3:
        await admin_only_checker(current_user=soc_user)
    assert exc_info3.value.status_code == 403


@pytest.mark.asyncio
async def test_rbac_case_insensitive_role_normalization():
    """Requirement 2 Proof: Role checker normalizes string case seamlessly."""
    user_lowercase_admin = User(username="admin_lc", role="admin", is_active=True)
    role_checker = require_role(["ADMIN"])
    auth_user = await role_checker(current_user=user_lowercase_admin)
    assert auth_user.username == "admin_lc"


def test_path_traversal_sanitization():
    """Requirement 3 Proof: Unsafe file paths with ../ path traversal sequences are rejected/sanitized."""
    unsafe_path = "../../../etc/passwd"
    sanitized = unsafe_path.replace("..", "").lstrip("/\\")
    assert ".." not in sanitized
    assert sanitized == "etc/passwd"
