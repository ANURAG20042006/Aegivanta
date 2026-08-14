"""
backend/app/api/v1/monitoring.py
================================
Continuous Asset Monitoring API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.monitoring import MonitoringCheck, MonitoringHistory
from backend.app.services.monitoring_service import MonitoringService, validate_target_url_safe

router = APIRouter(prefix="/monitoring", tags=["Continuous Asset Monitoring"])


class MonitoringCheckCreate(BaseModel):
    asset_id: str = Field(..., description="Target protected asset ID")
    target_url: str = Field(..., description="HTTP/HTTPS endpoint URL to monitor")
    monitor_type: str = Field("HTTP", description="Monitoring protocol (HTTP, HTTPS, TCP_PORT, DNS)")
    expected_status_code: int = Field(200, ge=100, le=599)
    timeout_seconds: float = Field(5.0, ge=1.0, le=10.0)
    interval_seconds: int = Field(60, ge=10, le=86400)
    is_enabled: bool = True


@router.get("/checks", summary="List All Monitoring Checks")
async def list_monitoring_checks(
    asset_id: Optional[str] = None,
    health_state: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all configured asset monitoring checks and current health states."""
    query = select(MonitoringCheck)
    if asset_id:
        query = query.where(MonitoringCheck.asset_id == asset_id)
    if health_state:
        query = query.where(MonitoringCheck.health_state == health_state.upper())
    query = query.order_by(MonitoringCheck.created_at.desc()).limit(limit)

    res = await db.execute(query)
    checks = res.scalars().all()
    return [
        {
            "id": c.id,
            "asset_id": c.asset_id,
            "monitor_type": c.monitor_type,
            "target_url": c.target_url,
            "expected_status_code": c.expected_status_code,
            "timeout_seconds": c.timeout_seconds,
            "interval_seconds": c.interval_seconds,
            "is_enabled": c.is_enabled,
            "health_state": c.health_state,
            "consecutive_failures": c.consecutive_failures,
            "last_check_at": c.last_check_at.isoformat() if c.last_check_at else None,
            "last_status_code": c.last_status_code,
            "last_response_time_ms": c.last_response_time_ms,
            "last_error_message": c.last_error_message,
            "dns_resolved_ip": c.dns_resolved_ip,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in checks
    ]


@router.post("/checks", status_code=status.HTTP_201_CREATED, summary="Create New Monitoring Check")
async def create_monitoring_check(
    payload: MonitoringCheckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Creates a new monitoring target check with strict SSRF validation."""
    is_safe, reason, resolved_ip, all_ips = validate_target_url_safe(payload.target_url, allow_private=False)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security Policy Rejection (SSRF Protection): {reason}"
        )

    check = MonitoringCheck(
        asset_id=payload.asset_id,
        target_url=payload.target_url,
        monitor_type=payload.monitor_type.upper(),
        expected_status_code=payload.expected_status_code,
        timeout_seconds=payload.timeout_seconds,
        interval_seconds=payload.interval_seconds,
        is_enabled=payload.is_enabled,
        health_state="HEALTHY",
        dns_resolved_ip=resolved_ip
    )
    db.add(check)
    await db.commit()
    await db.refresh(check)

    return {
        "id": check.id,
        "asset_id": check.asset_id,
        "target_url": check.target_url,
        "health_state": check.health_state,
        "is_enabled": check.is_enabled,
        "dns_resolved_ip": resolved_ip
    }


@router.get("/checks/{check_id}/history", summary="Get Monitoring Time-Series History")
async def get_check_history(
    check_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves time-series latency and response history for a specific monitor."""
    query = (
        select(MonitoringHistory)
        .where(MonitoringHistory.check_id == check_id)
        .order_by(MonitoringHistory.timestamp.desc())
        .limit(limit)
    )
    res = await db.execute(query)
    history = res.scalars().all()
    return [
        {
            "id": h.id,
            "timestamp": h.timestamp.isoformat() if h.timestamp else None,
            "status_code": h.status_code,
            "response_time_ms": h.response_time_ms,
            "is_success": h.is_success,
            "error_message": h.error_message
        }
        for h in history
    ]


@router.post("/checks/{check_id}/run", summary="Trigger On-Demand Health Diagnostic Check")
async def run_check_now(
    check_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Triggers an immediate execution of an asset health check."""
    query = select(MonitoringCheck).where(MonitoringCheck.id == check_id)
    res = await db.execute(query)
    check = res.scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitoring check not found.")

    result = await MonitoringService.run_check(check, db, allow_private=False)
    await db.commit()
    return result


@router.delete("/checks/{check_id}", summary="Delete Monitoring Check")
async def delete_monitoring_check(
    check_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Deletes a monitoring target."""
    query = select(MonitoringCheck).where(MonitoringCheck.id == check_id)
    res = await db.execute(query)
    check = res.scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitoring check not found.")

    await db.delete(check)
    await db.commit()
    return {"status": "success", "message": f"Monitoring check {check_id} deleted."}
