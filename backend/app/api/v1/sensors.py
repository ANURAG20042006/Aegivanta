from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.models.sensor import Sensor
from backend.app.services.sensor_service import SensorService
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/sensors", tags=["Sensors & Agents"])


class EnrollSensorRequest(BaseModel):
    name: str
    hostname: str
    ip_address: str
    os_type: Optional[str] = "linux"
    capabilities: Optional[Dict[str, Any]] = None


class SensorEnrollResponse(BaseModel):
    id: str
    name: str
    hostname: str
    ip_address: str
    os_type: str
    status: str
    enrollment_token: str  # Plain token returned only once
    created_at: datetime


class SensorListItem(BaseModel):
    id: str
    name: str
    hostname: str
    ip_address: str
    os_type: str
    sensor_version: str
    status: str
    last_heartbeat: datetime
    created_at: datetime


class SensorHeartbeatRequest(BaseModel):
    token: str
    stats: Optional[Dict[str, Any]] = None


@router.post("/enroll", response_model=SensorEnrollResponse, status_code=status.HTTP_201_CREATED, summary="Enroll New Customer Telemetry Sensor")
async def enroll_sensor(
    payload: EnrollSensorRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Enrolls a new customer endpoint sensor. Plain enrollment token is provided only once."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    sensor, raw_token = await SensorService.enroll_sensor(
        db=db,
        tenant_id=context.tenant_id,
        name=payload.name,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        os_type=payload.os_type or "linux",
        capabilities=payload.capabilities
    )

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"sensor:{sensor.id}",
        action=f"Enrolled sensor '{sensor.name}' on host '{sensor.hostname}'"
    )

    await db.commit()
    return SensorEnrollResponse(
        id=sensor.id,
        name=sensor.name,
        hostname=sensor.hostname,
        ip_address=sensor.ip_address,
        os_type=sensor.os_type,
        status=sensor.status,
        enrollment_token=raw_token,
        created_at=sensor.created_at
    )


@router.post("/{sensor_id}/heartbeat", summary="Process Sensor Agent Heartbeat")
async def sensor_heartbeat(
    sensor_id: str,
    payload: SensorHeartbeatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Receives heartbeat from sensor agent and refreshes status to ONLINE."""
    sensor = await SensorService.process_heartbeat(
        db=db,
        sensor_id=sensor_id,
        raw_token=payload.token,
        telemetry_stats=payload.stats
    )
    await db.commit()
    return {"status": "ACK", "sensor_id": sensor.id, "last_heartbeat": sensor.last_heartbeat.isoformat()}


@router.get("", response_model=List[SensorListItem], summary="List Enrolled Sensors")
async def list_sensors(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists all enrolled sensors for the active tenant."""
    if not context.tenant_id:
        return []

    sensors = await SensorService.list_sensors(db, context.tenant_id)
    return [
        SensorListItem(
            id=s.id,
            name=s.name,
            hostname=s.hostname,
            ip_address=s.ip_address,
            os_type=s.os_type,
            sensor_version=s.sensor_version,
            status=s.status,
            last_heartbeat=s.last_heartbeat,
            created_at=s.created_at
        )
        for s in sensors
    ]


@router.delete("/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke Sensor Agent")
async def revoke_sensor(
    sensor_id: str,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Revokes sensor enrollment and stops telemetry ingestion."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    success = await SensorService.revoke_sensor(db, sensor_id, context.tenant_id)
    if not success:
        raise SentinelAIException(status_code=404, detail="Sensor not found or not owned by tenant.")

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"sensor:{sensor_id}",
        action=f"Revoked sensor enrollment ID '{sensor_id}'"
    )
    await db.commit()
