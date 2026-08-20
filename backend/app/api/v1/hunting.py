"""
backend/app/api/v1/hunting.py
=============================
Phase 3.8 Advanced Threat Hunting, DSL Queries, and Modular Hunt Rule Endpoints.
"""

from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.core.rate_limit import hunting_rate_limit
from backend.app.services.threat_hunting_service import ThreatHuntingService
from backend.app.hunting import hunt_rule_registry

router = APIRouter(prefix="/hunting", tags=["Threat Hunting Engine"])


# ==============================================================================
# SCHEMAS
# ==============================================================================

class HuntingDSLFilter(BaseModel):
    field: str
    operator: str = "equals"
    value: Any


class HuntingDSLQueryRequest(BaseModel):
    entity: str = Field(default="events", description="Target entity: events, alerts, incidents, iocs")
    time_range: Optional[Union[Dict[str, str], str]] = None
    start_time: Optional[str] = None
    filters: Union[List[HuntingDSLFilter], Dict[str, Any]] = Field(default_factory=list)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    query_id: Optional[str] = None


class RunHuntRequest(BaseModel):
    events: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None


class SaveQueryTemplateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    query_definition: Dict[str, Any]


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.post("/query", summary="Execute Structured Threat Hunting DSL Query", dependencies=[Depends(hunting_rate_limit)])
async def execute_hunt(
    payload: HuntingDSLQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Executes a typed, bounded threat hunting search across security telemetry."""
    try:
        raw_filters: List[Dict[str, Any]] = []
        if isinstance(payload.filters, dict):
            for k, v in payload.filters.items():
                raw_filters.append({"field": k, "operator": "equals", "value": v})
        elif isinstance(payload.filters, list):
            for f in payload.filters:
                if isinstance(f, HuntingDSLFilter):
                    raw_filters.append(f.model_dump())
                elif isinstance(f, dict):
                    raw_filters.append(f)

        t_range = None
        if isinstance(payload.time_range, dict):
            t_range = payload.time_range
        elif isinstance(payload.time_range, str):
            t_range = {"start": payload.start_time} if payload.start_time else None

        return await ThreatHuntingService.execute_dsl_query(
            entity=payload.entity,
            time_range=t_range,
            filters=raw_filters,
            limit=payload.limit,
            offset=payload.offset,
            executed_by=current_user.username,
            query_id=payload.query_id,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/hunts", summary="List All Modular Threat Hunting Rules")
async def list_threat_hunts(
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists all 10 production threat hunting rules with MITRE ATT&CK technique mappings."""
    return hunt_rule_registry.list_hunts()


@router.get("/hunts/{hunt_id}", summary="Get Threat Hunt Rule Details")
async def get_threat_hunt_details(
    hunt_id: str,
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves specific threat hunt rule metadata and evaluation logic."""
    h = hunt_rule_registry.get_hunt(hunt_id)
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Threat hunt rule '{hunt_id}' not found.")
    return {
        "hunt_id": h.hunt_id,
        "name": h.name,
        "description": h.description,
        "severity": h.severity,
        "mitre_technique": h.mitre_technique,
        "tactic": h.tactic
    }


@router.post("/run/{hunt_id}", summary="Execute Modular Threat Hunt Rule")
async def run_threat_hunt(
    hunt_id: str,
    payload: RunHuntRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Runs a specific hunt rule against provided or recent historical telemetry events."""
    events = payload.events
    if events is None:
        # Fetch recent security events from database
        query_res = await ThreatHuntingService.execute_dsl_query(
            entity="events",
            limit=500,
            db=db
        )
        events = query_res.get("results", [])

    try:
        findings = hunt_rule_registry.run_hunt(hunt_id, events, payload.context)
        return {
            "hunt_id": hunt_id.upper(),
            "total_findings": len(findings),
            "events_evaluated": len(events),
            "executed_by": current_user.username,
            "findings": findings
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/saved", summary="List Saved Threat Hunting Queries")
async def list_saved_queries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists saved threat hunting search templates."""
    queries = await ThreatHuntingService.list_saved_queries(db)
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
    """Saves a reusable parameterized threat hunting query."""
    from backend.app.models.hunting import HuntingQuery
    import uuid
    from datetime import datetime, timezone

    query = HuntingQuery(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        query_definition=payload.query_definition,
        created_by=current_user.username,
        is_saved=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(query)
    await db.commit()
    await db.refresh(query)
    return {
        "status": "SUCCESS",
        "id": query.id,
        "name": query.name,
        "created_at": query.created_at.isoformat()
    }
