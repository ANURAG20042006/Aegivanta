import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.services.scim_service import SCIMService
from backend.app.core.exceptions import SentinelAIException, AuthenticationError

logger = logging.getLogger("SentinelAI.SCIMRouter")

router = APIRouter(prefix="/scim/v2", tags=["SCIM 2.0 Identity Provisioning"])


async def get_scim_config(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticates inbound SCIM request via Bearer token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized SCIM request. Bearer token required.")

    token = auth_header.replace("Bearer ", "").strip()
    config = await SCIMService.authenticate_scim_request(db, token)
    if not config:
        raise HTTPException(status_code=401, detail="Invalid SCIM Bearer token.")
    return config


@router.post("/Users", status_code=status.HTTP_201_CREATED, summary="SCIM 2.0 Create / Provision User")
async def scim_create_user(
    request: Request,
    config = Depends(get_scim_config),
    db: AsyncSession = Depends(get_db)
):
    """RFC 7644 SCIM 2.0 User Provisioning Endpoint."""
    user_payload = await request.json()
    result = await SCIMService.provision_user(db, config.organization_id, user_payload)
    await db.commit()
    return result


@router.delete("/Users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="SCIM 2.0 Deactivate User")
async def scim_delete_user(
    user_id: str,
    config = Depends(get_scim_config),
    db: AsyncSession = Depends(get_db)
):
    """RFC 7644 SCIM 2.0 User Deprovisioning / Deactivation Endpoint."""
    success = await SCIMService.deactivate_user(db, config.organization_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found.")
    await db.commit()
