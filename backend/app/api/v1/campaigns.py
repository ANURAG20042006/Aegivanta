"""
backend/app/api/v1/campaigns.py
===============================
API Endpoints for Multi-Incident Correlated Campaign Detection.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["Campaign Correlation Engine"])


@router.get("", summary="List Detected Coordinated Campaigns")
async def list_campaigns(
    lookback_hours: int = 48,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns detected multi-incident campaigns clustered by shared evidence and infrastructure."""
    return await CampaignService.detect_campaigns(lookback_hours=lookback_hours, db=db)
