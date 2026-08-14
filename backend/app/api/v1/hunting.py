"""
backend/app/api/v1/hunting.py
=============================
API Endpoints for Advanced Threat Hunting, Parameterized Searches & Saved Queries.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.core.rate_limit import hunting_rate_limit
from backend.app.services.hunting_service import HuntingService

router = APIRouter(prefix="/hunting", tags=["Threat Hunting Engine"])


class HuntingQueryRequest(BaseModel):
    entity: str = Field(default="alerts", description="Target entity: alerts, incidents, iocs")
    time_range: str = Field(default="24h", description="Time range: 1h, 24h, 7d, 30d, custom")
    start_time: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    query_id: Optional[str] = None


class SaveQueryTemplateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    query_definition: Dict[str, Any]


@router.post("/query", summary="Execute Parameterized Threat Hunt", dependencies=[Depends(hunting_rate_limit)])
async def execute_hunt(
    payload: HuntingQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Executes a bounded, parameterized threat hunt across security entities."""
    return await HuntingService.execute_hunting_query(
        query_def=payload.model_dump(),
        executed_by=current_user.username,
        query_id=payload.query_id,
        db=db
    )


@router.get("/saved", summary="List Saved Threat Hunting Queries")
async def list_saved_queries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists saved threat hunting search templates."""
    queries = await HuntingService.list_saved_queries(db)
    return [
        {
            "id": q.id,
            "name": q.name,
            "description": q.description,
            "query_definition": q.query_definition,
            "created_by": q.created_by,
            "created_at": q.created_at.isoformat() if q.created_at else None
        }
        for q in queries
    ]


@router.post("/saved", summary="Save Threat Hunting Query Template", status_code=status.HTTP_201_CREATED)
async def save_query_template(
    payload: SaveQueryTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Saves a parameterized query template (Analyst/Admin only)."""
    q = await HuntingService.create_saved_query(
        name=payload.name,
        description=payload.description,
        query_definition=payload.query_definition,
        created_by=current_user.username,
        db=db
    )
    return {
        "id": q.id,
        "name": q.name,
        "description": q.description,
        "created_by": q.created_by,
        "created_at": q.created_at.isoformat() if q.created_at else None
    }
