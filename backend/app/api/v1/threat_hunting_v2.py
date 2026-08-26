"""
backend/app/api/v1/threat_hunting_v2.py
=======================================
Phase 26.8 Threat Hunting Workbench V2 API Endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.threat_hunting_v2_service import ThreatHuntingV2Service

router = APIRouter(prefix="/hunting/v2", tags=["Threat Hunting Workbench V2"])


class CreateSavedQueryRequest(BaseModel):
    name: str = Field(..., example="Outbound C2 Port 8443 Probe")
    query_string: str = Field(..., example="destination_port == 8443 and bytes_sent > 1000000")
    target_data_source: str = Field(default="TELEMETRY", example="NETWORK")
    description: Optional[str] = None
    mitre_attack_techniques: List[str] = Field(default_factory=list, example=["T1071.001"])
    tags: List[str] = Field(default_factory=list, example=["hunt", "c2"])


class ExecuteHuntRequest(BaseModel):
    hypothesis: str = Field(..., example="Threat actor using encoded PowerShell to download secondary payloads.")
    query_string: str = Field(..., example="process_name == 'powershell.exe' and cmdline contains '-enc'")
    time_range_hours: int = Field(default=24, ge=1, le=720)
    target_source: str = Field(default="ENDPOINT", example="ENDPOINT")
    entity_filters: Dict[str, Any] = Field(default_factory=dict, example={"hostname": "WKS-EXEC-01"})
    linked_case_id: Optional[str] = None
    saved_query_id: Optional[str] = None


@router.get("/saved", summary="List Saved Threat Hunting Queries")
async def list_saved_queries(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists all reusable threat hunting query templates for the tenant."""
    tenant_id = get_enforced_tenant_id(context)
    return await ThreatHuntingV2Service.list_saved_queries(db, tenant_id)


@router.post("/saved", summary="Save Threat Hunting Query Template")
async def create_saved_query(
    req: CreateSavedQueryRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Saves a reusable parameterized threat hunting query."""
    tenant_id = get_enforced_tenant_id(context)
    saved = await ThreatHuntingV2Service.create_saved_query(
        db=db,
        tenant_id=tenant_id,
        name=req.name,
        query_string=req.query_string,
        target_data_source=req.target_data_source,
        description=req.description,
        mitre_attack_techniques=req.mitre_attack_techniques,
        tags=req.tags
    )
    return {
        "id": saved.id,
        "name": saved.name,
        "query_string": saved.query_string,
        "target_data_source": saved.target_data_source,
        "created_at": saved.created_at.isoformat()
    }


@router.post("/search", summary="Execute Threat Hunting Search")
async def execute_hunt(
    req: ExecuteHuntRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes a threat hunting query against normalized telemetry across the lookback window."""
    tenant_id = get_enforced_tenant_id(context)
    return await ThreatHuntingV2Service.execute_hunt(
        db=db,
        tenant_id=tenant_id,
        hypothesis=req.hypothesis,
        query_string=req.query_string,
        time_range_hours=req.time_range_hours,
        target_source=req.target_source,
        entity_filters=req.entity_filters,
        linked_case_id=req.linked_case_id,
        saved_query_id=req.saved_query_id
    )
