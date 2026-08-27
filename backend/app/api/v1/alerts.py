"""
backend/app/api/v1/alerts.py
============================
Live Security Alerts API Endpoints.
Supports filtering, status lifecycle triage, and aggregation for SOC operations.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.core.auth import get_current_user, require_role
from backend.app.core.logging import logger
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.schemas.alert import (
    AlertResponse, AlertStatusUpdate, AlertListResponse, AlertStatsResponse
)


router = APIRouter(prefix="/alerts", tags=["Live Security Alerts"])


@router.get("", response_model=AlertListResponse, summary="Search and Paginate Security Alerts")
async def list_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    asset_id: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    attack_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paginated list of security alerts with server-side filters."""
    filters = []
    if severity:
        filters.append(func.lower(Alert.severity) == severity.lower())
    if status_filter:
        filters.append(func.lower(Alert.status) == status_filter.lower())
    if asset_id:
        filters.append(Alert.asset_id == asset_id)
    if source_ip:
        filters.append(Alert.source_ip == source_ip)
    if attack_type:
        filters.append(Alert.attack_type == attack_type)

    total_stmt = select(func.count(Alert.id)).where(*filters)
    total = (await db.execute(total_stmt)).scalar_one()

    offset = (page - 1) * size
    query = select(Alert).where(*filters).order_by(Alert.timestamp.desc()).offset(offset).limit(size)
    result = (await db.execute(query)).scalars().all()

    return AlertListResponse(
        total=total,
        page=page,
        size=size,
        items=result
    )


@router.get("/summary/stats", response_model=AlertStatsResponse, summary="Get Live Alerts Aggregate Statistics")
async def get_alerts_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Computes real-time alert statistics for SOC monitoring dashboards."""
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    total_active = (await db.execute(
        select(func.count(Alert.id)).where(Alert.status.in_(["new", "acknowledged", "investigating"]))
    )).scalar_one()

    critical = (await db.execute(
        select(func.count(Alert.id)).where(and_(Alert.severity == "critical", Alert.status != "resolved"))
    )).scalar_one()

    high = (await db.execute(
        select(func.count(Alert.id)).where(and_(Alert.severity == "high", Alert.status != "resolved"))
    )).scalar_one()

    new_count = (await db.execute(
        select(func.count(Alert.id)).where(Alert.status == "new")
    )).scalar_one()

    last_hour = (await db.execute(
        select(func.count(Alert.id)).where(Alert.timestamp >= one_hour_ago)
    )).scalar_one()

    # Severity distribution
    sev_query = select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)
    sev_rows = (await db.execute(sev_query)).all()
    sev_breakdown = {row[0]: row[1] for row in sev_rows}

    return AlertStatsResponse(
        total_active_alerts=total_active,
        critical_alerts_count=critical,
        high_alerts_count=high,
        new_alerts_count=new_count,
        alerts_last_hour=last_hour,
        severity_breakdown=sev_breakdown
    )


@router.get("/{alert_id}", response_model=AlertResponse, summary="Get Alert Details")
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves full details for a specific security alert by UUID or ALT code."""
    stmt = select(Alert).where(or_(Alert.id == alert_id, Alert.alert_id == alert_id))
    alert = (await db.execute(stmt)).scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return alert


@router.patch("/{alert_id}/status", response_model=AlertResponse, summary="Update Alert Triage Status")
async def update_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Updates alert triage status (new -> acknowledged -> investigating -> resolved -> dismissed)."""
    stmt = select(Alert).where(or_(Alert.id == alert_id, Alert.alert_id == alert_id))
    alert = (await db.execute(stmt)).scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

    old_status = alert.status
    alert.status = payload.status
    alert.updated_at = datetime.now(timezone.utc)

    # If alert is linked to an incident, append a timeline event
    if alert.incident_id:
        timeline_event = IncidentTimelineEvent(
            incident_id=alert.incident_id,
            timestamp=datetime.now(timezone.utc),
            event_type="STATUS_CHANGE",
            title=f"Alert {alert.alert_id} Marked as {payload.status.upper()}",
            description=f"Analyst @{current_user.username} updated alert status from {old_status} to {payload.status}. Notes: {payload.notes or 'None'}",
            actor=current_user.username
        )
        db.add(timeline_event)

    audit = AuditLog(
        user_id=current_user.id,
        action="UPDATE_ALERT_STATUS",
        resource="ALERTS",
        details={"message": f"Changed status of alert '{alert.alert_id}' from '{old_status}' to '{payload.status}'."}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(alert)

    logger.info("Alert %s status updated to %s by %s", alert.alert_id, payload.status, current_user.username)
    return alert
