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


# ==============================================================================
# PHASE 3.5 ATTACK GRAPH ANALYTICS & LATERAL MOVEMENT ENDPOINTS
# ==============================================================================

from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.services.lateral_movement_service import LateralMovementDetector


class LateralMovementDetectRequest(BaseModel):
    events: Optional[List[Dict[str, Any]]] = Field(None, description="Explicit event list to analyze")
    max_dwell_hours: float = Field(24.0, ge=0.1, le=168.0, description="Max dwell hours between consecutive hops")
    min_chain_length: int = Field(2, ge=2, le=10, description="Minimum causal hop length")


class AttackPathFindRequest(BaseModel):
    source_id: str = Field(..., description="Origin graph node ID (e.g. 'asset-1' or 'ioc-1')")
    target_id: str = Field(..., description="Destination target node ID (e.g. 'asset-5')")
    max_hops: int = Field(6, ge=1, le=12, description="Maximum traversal search depth")


class BlastRadiusRequest(BaseModel):
    origin_node_id: str = Field(..., description="Starting compromised node ID")
    max_depth: int = Field(3, ge=1, le=8, description="Maximum forward BFS reachability depth")


@router.post("/lateral-movement/detect", summary="Detect Multi-Hop Lateral Movement Paths")
async def detect_lateral_movement(
    payload: Optional[LateralMovementDetectRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """
    Analyzes temporal incident and telemetry events to identify multi-hop lateral movement chains,
    calculates hop velocity, maps MITRE ATT&CK techniques, and recommends intermediate choke points.
    """
    req = payload or LateralMovementDetectRequest()
    events = req.events

    if events is None:
        # Load from DB incidents and alerts
        events = []
        res_inc = await db.execute(select(Incident).order_by(desc(Incident.timestamp)).limit(50))
        for inc in res_inc.scalars().all():
            if inc.source_ip and inc.destination_ip:
                events.append({
                    "id": inc.id,
                    "source_ip": inc.source_ip,
                    "destination_ip": inc.destination_ip,
                    "timestamp": inc.timestamp,
                    "risk_score": inc.risk_score or 75.0,
                    "attack_type": inc.attack_type,
                    "severity": inc.severity
                })

    chains = LateralMovementDetector.detect_lateral_movement_chains(
        events=events,
        max_dwell_hours=req.max_dwell_hours,
        min_chain_length=req.min_chain_length
    )

    return {
        "total_chains_detected": len(chains),
        "chains": chains
    }


@router.post("/paths/find", summary="Find Multi-Hop Attack Trajectories & Shortest/Highest-Risk Paths")
async def find_attack_paths(
    payload: AttackPathFindRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Computes simple directed paths, shortest paths, and highest-risk attack paths between two graph nodes."""
    return await ThreatGraphService.find_attack_paths(
        source_id=payload.source_id,
        target_id=payload.target_id,
        max_hops=payload.max_hops,
        db=db
    )


@router.get("/chokepoints", summary="Identify Network Choke Points & Centrality Bridges")
async def get_chokepoints(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Ranks top architectural choke points by betweenness and degree centrality for strategic network isolation."""
    return await ThreatGraphService.calculate_chokepoints(top_n=limit, db=db)


@router.post("/blast-radius", summary="Calculate Compromise Blast Radius & Crown Jewel Exposure")
async def calculate_blast_radius(
    payload: BlastRadiusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Calculates forward reachability blast radius, exposed assets, and Crown Jewel Exposure Index from an origin node."""
    return await ThreatGraphService.calculate_blast_radius(
        origin_node_id=payload.origin_node_id,
        max_depth=payload.max_depth,
        db=db
    )


@router.get("/analytics", summary="Get Attack Graph Topological Analytics")
async def get_graph_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves graph density, node/relationship distributions, and degree metrics."""
    return await ThreatGraphService.get_graph_analytics(db=db)

