from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.investigation_search_service import InvestigationSearchService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/investigations", tags=["Threat Investigation Search"])


class SearchRequestPayload(BaseModel):
    query: Optional[str] = None
    entity_types: Optional[List[str]] = None
    severity: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    asset_id: Optional[str] = None
    lookback_days: Optional[int] = 30
    page: Optional[int] = 1
    limit: Optional[int] = 25


@router.post("/search", summary="Execute Unified Multi-Entity Threat Search")
async def execute_search_post(
    payload: SearchRequestPayload,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes indexed, bounded search across alerts, incidents, assets, threat intel, and detection rules."""
    return await InvestigationSearchService.global_search(
        db=db,
        tenant_id=context.tenant_id,
        query=payload.query,
        entity_types=payload.entity_types,
        severity=payload.severity,
        source_ip=payload.source_ip,
        destination_ip=payload.destination_ip,
        asset_id=payload.asset_id,
        lookback_days=payload.lookback_days or 30,
        page=payload.page or 1,
        limit=payload.limit or 25
    )


@router.get("/search", summary="Unified Threat Search (GET)")
async def execute_search_get(
    q: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    destination_ip: Optional[str] = Query(None),
    asset_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Query parameter version of unified threat investigation search."""
    return await InvestigationSearchService.global_search(
        db=db,
        tenant_id=context.tenant_id,
        query=q,
        severity=severity,
        source_ip=source_ip,
        destination_ip=destination_ip,
        asset_id=asset_id,
        page=page,
        limit=limit
    )
