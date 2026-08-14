"""
backend/app/api/v1/threat_graph.py
==================================
API Endpoints for Threat Intelligence Graph Topology and Evidence Inspection.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.core.rate_limit import graph_rate_limit
from backend.app.services.threat_graph_service import ThreatGraphService

router = APIRouter(prefix="/threat-graph", tags=["Threat Intelligence Graph"])


@router.get("", summary="Get Threat Intelligence Graph Topology", dependencies=[Depends(graph_rate_limit)])
async def get_graph(
    limit: int = 150,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns graph nodes and evidence-backed relationship edges."""
    return await ThreatGraphService.get_graph_topology(limit=limit, db=db)


@router.get("/nodes/{node_id}/evidence", summary="Get Node Evidence Drilldown")
async def get_node_evidence(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves underlying evidence records supporting a graph node."""
    return await ThreatGraphService.get_node_evidence(node_id, db)
