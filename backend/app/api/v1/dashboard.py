"""
backend/app/api/v1/dashboard.py
===============================
Production REST Endpoints for SOC Command Center Aggregation & Visibility.
Optimized batch aggregations eliminating N+1 API queries.
Strict JWT Authentication and Normalized RBAC Enforcement.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.services.soc_dashboard_service import SOCDashboardService

router = APIRouter(prefix="/dashboard", tags=["SOC Command Center Dashboard"])


@router.get("/overview", summary="Get Aggregated SOC Overview KPIs")
async def get_soc_overview(
    lookback_days: int = Query(default=30, ge=1, le=365, description="Lookback window in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """
    Returns unified SOC Operations Overview KPIs:
    Total, Open, Critical, High incidents, MTTD, MTTA, MTTR, MTT-Resolve,
    active investigations, SOAR actions, IOC matches, detection rate,
    false-positive rate, event ingestion rate, MITRE coverage, and system status.
    """
    return await SOCDashboardService.get_overview_metrics(db=db, lookback_days=lookback_days)


@router.get("/incidents", summary="Query, Filter & Paginate Incidents for Incident Command Center")
async def get_dashboard_incidents(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=25, ge=1, le=100, description="Items per page"),
    severity: Optional[str] = Query(default=None, max_length=20, description="Filter by severity (Low, Medium, High, Critical)"),
    status: Optional[str] = Query(default=None, max_length=30, description="Filter by incident status"),
    attack_type: Optional[str] = Query(default=None, max_length=50, description="Filter by attack classification"),
    search: Optional[str] = Query(default=None, max_length=100, description="Search across IPs, incident codes, and descriptions"),
    sort_by: str = Query(default="risk_score", description="Sort field (risk_score, timestamp, severity, status, alert_count, source_ip)"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort direction (asc, desc)"),
    lookback_hours: Optional[int] = Query(default=None, ge=1, le=8760, description="Optional relative time filter in hours"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """
    Provides rich server-side filtered, sorted, and paginated incident records
    with asset criticality and MITRE/IOC enrichment.
    """
    return await SOCDashboardService.get_dashboard_incidents(
        db=db,
        page=page,
        limit=limit,
        severity=severity,
        status_filter=status,
        attack_type=attack_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        lookback_hours=lookback_hours
    )


@router.get("/detections", summary="Get Aggregated Threat Detections & Rule Statistics")
async def get_dashboard_detections(
    lookback_days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """Returns detection volume, attack distribution, severity breakdown, and recent telemetry."""
    return await SOCDashboardService.get_dashboard_detections(db=db, lookback_days=lookback_days)


@router.get("/threat-intel", summary="Get Threat Intelligence Health & Fast Cache Statistics")
async def get_dashboard_threat_intel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """Returns IOC repository statistics, feed synchronization health, and Fast IOC Cache performance."""
    return await SOCDashboardService.get_dashboard_threat_intel(db=db)


@router.get("/response", summary="Get Autonomous SOAR Response Statistics & Action Approvals")
async def get_dashboard_response(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """Returns pending approvals, executing actions, execution success rates, and response latencies."""
    return await SOCDashboardService.get_dashboard_response(db=db)


@router.get("/investigations", summary="Get Active Investigation Cases & Analyst Workload")
async def get_dashboard_investigations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """Returns case state distribution, priority breakdown, recent cases, and workload distribution."""
    return await SOCDashboardService.get_dashboard_investigations(db=db)


@router.get("/mitre", summary="Get Enterprise MITRE ATT&CK Matrix Coverage Analytics")
async def get_dashboard_mitre(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """Returns matrix coverage percentage, covered vs uncovered techniques, and frequency metrics."""
    return await SOCDashboardService.get_dashboard_mitre(db=db)


@router.get("/system-health", summary="Get Unified Platform Subsystem Health & Latency Metrics")
async def get_dashboard_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> Dict[str, Any]:
    """
    Returns live health and measured latency across API, PostgreSQL, Redis,
    Inference, Workers, WebSockets, and Ingress. Never leaks credentials.
    """
    return await SOCDashboardService.get_dashboard_system_health(db=db)


@router.get("/events", summary="Get Real-Time SOC Event Stream Records from Ring Buffer")
async def get_dashboard_events(
    limit: int = Query(default=50, ge=1, le=200, description="Max number of events to return"),
    type: Optional[str] = Query(default=None, description="Filter by SOC event type"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    since: Optional[str] = Query(default=None, description="ISO-8601 timestamp cutoff"),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
) -> List[Dict[str, Any]]:
    """Returns recent SOC events from in-memory ring buffer with deduplication and sequence ordering."""
    return SOCDashboardService.get_dashboard_events(
        limit=limit,
        event_type=type,
        severity=severity,
        since_iso=since
    )
