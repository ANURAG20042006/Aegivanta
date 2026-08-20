from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.models.sensor import Sensor
from backend.app.services.sensor_service import SensorService
from backend.app.services.telemetry_ingestion_service import TelemetryIngestionService
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException, AuthenticationError

router = APIRouter(prefix="/sensors", tags=["Sensors & Ingestion Ecosystem"])


class EnrollSensorRequest(BaseModel):
    name: str
    hostname: str
    ip_address: str
    os_type: Optional[str] = "linux"
    sensor_type: Optional[str] = "ENDPOINT_EDR"
    capabilities: Optional[Dict[str, Any]] = None


class SensorEnrollResponse(BaseModel):
    id: str
    name: str
    hostname: str
    ip_address: str
    os_type: str
    sensor_type: str
    sensor_version: str
    status: str
    health_score: int
    enrollment_token: str  # Plain token returned only once
    created_at: datetime


class SensorListItem(BaseModel):
    id: str
    name: str
    hostname: str
    ip_address: str
    os_type: str
    sensor_type: str
    sensor_version: str
    status: str
    health_score: int
    offline_buffer_events: int
    upgrade_status: str
    last_heartbeat: datetime
    created_at: datetime


class SensorHeartbeatRequest(BaseModel):
    token: str
    stats: Optional[Dict[str, Any]] = None


class UpgradeSensorRequest(BaseModel):
    target_version: str


@router.post("/enroll", response_model=SensorEnrollResponse, status_code=status.HTTP_201_CREATED, summary="Enroll New Customer Telemetry Sensor")
async def enroll_sensor(
    payload: EnrollSensorRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Enrolls a new customer endpoint or network sensor with 90-day cryptographic rotating token."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    sensor, raw_token = await SensorService.enroll_sensor(
        db=db,
        tenant_id=context.tenant_id,
        name=payload.name,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        os_type=payload.os_type or "linux",
        sensor_type=payload.sensor_type or "ENDPOINT_EDR",
        capabilities=payload.capabilities
    )

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"sensor:{sensor.id}",
        action=f"Enrolled {sensor.sensor_type} sensor '{sensor.name}' on host '{sensor.hostname}'"
    )

    await db.commit()
    return SensorEnrollResponse(
        id=sensor.id,
        name=sensor.name,
        hostname=sensor.hostname,
        ip_address=sensor.ip_address,
        os_type=sensor.os_type,
        sensor_type=sensor.sensor_type,
        sensor_version=sensor.sensor_version,
        status=sensor.status,
        health_score=sensor.health_score,
        enrollment_token=raw_token,
        created_at=sensor.created_at
    )


@router.post("/ingest", summary="Ingest Compressed Batch Telemetry from Agent")
async def ingest_telemetry(
    request: Request,
    x_sensor_id: str = Header(..., alias="X-Sensor-ID"),
    x_sensor_token: str = Header(..., alias="X-Sensor-Token"),
    content_encoding: Optional[str] = Header(None, alias="Content-Encoding"),
    db: AsyncSession = Depends(get_db)
):
    """
    High-throughput compressed telemetry ingestion endpoint.
    Accepts gzip/deflate batches of Network flows, Auth events, DNS, HTTP, and Process events.
    """
    # 1. Authenticate Sensor
    stmt = select(Sensor).where(Sensor.id == x_sensor_id)
    res = await db.execute(stmt)
    sensor = res.scalar_one_or_none()

    if not sensor or sensor.status == "REVOKED":
        raise AuthenticationError(detail="Sensor agent not found or revoked.")

    token_hash = SensorService._hash_token(x_sensor_token)
    if sensor.enrollment_token_hash != token_hash:
        raise AuthenticationError(detail="Invalid sensor authentication token.")

    # 2. Decompress and Validate Payload
    body_bytes = await request.body()
    batch_json = TelemetryIngestionService.decompress_payload(body_bytes, content_encoding)

    # 3. Process Batch (Deduplication, Sequence Sorting, Usage Metering)
    result = await TelemetryIngestionService.process_telemetry_batch(db, sensor, batch_json)
    await db.commit()
    return result


@router.post("/{sensor_id}/heartbeat", summary="Process Sensor Agent Heartbeat")
async def sensor_heartbeat(
    sensor_id: str,
    payload: SensorHeartbeatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Receives heartbeat from sensor agent and refreshes status to ONLINE with health telemetry."""
    sensor = await SensorService.process_heartbeat(
        db=db,
        sensor_id=sensor_id,
        raw_token=payload.token,
        telemetry_stats=payload.stats
    )
    await db.commit()
    return {
        "status": "ACK",
        "sensor_id": sensor.id,
        "health_score": sensor.health_score,
        "upgrade_status": sensor.upgrade_status,
        "target_version": sensor.target_version,
        "last_heartbeat": sensor.last_heartbeat.isoformat()
    }


@router.post("/{sensor_id}/rotate-token", summary="Rotate Sensor Enrollment Token")
async def rotate_sensor_token(
    sensor_id: str,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Rotates cryptographic credentials for a sensor agent and returns the new token once."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    sensor, new_token = await SensorService.rotate_token(db, sensor_id, context.tenant_id)
    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"sensor:{sensor_id}",
        action=f"Rotated enrollment token for sensor '{sensor.name}'"
    )
    await db.commit()
    return {"sensor_id": sensor.id, "new_token": new_token, "expires_at": sensor.token_expires_at.isoformat()}


@router.post("/{sensor_id}/upgrade", summary="Schedule OTA Version Upgrade for Sensor")
async def schedule_sensor_upgrade(
    sensor_id: str,
    payload: UpgradeSensorRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Schedules an over-the-air version upgrade for an active sensor agent."""
    if not context.tenant_id:
        raise SentinelAIException(status_code=400, detail="Active tenant required.")

    sensor = await SensorService.schedule_upgrade(db, sensor_id, context.tenant_id, payload.target_version)
    await db.commit()
    return {"sensor_id": sensor.id, "upgrade_status": sensor.upgrade_status, "target_version": sensor.target_version}


@router.get("/fleet/health", summary="Get Fleet Health Analytics")
async def get_fleet_health(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates overall sensor fleet health, online ratios, and offline buffering queue metrics."""
    if not context.tenant_id:
        return {"total_sensors": 0, "online_count": 0, "average_health_score": 100}

    return await SensorService.get_fleet_health(db, context.tenant_id)


@router.get("/{sensor_id}/install-command", summary="Get Cross-Platform Sensor Install Script")
async def get_sensor_install_command(
    sensor_id: str,
    os_type: str = "linux",
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates one-click deployment command for Linux, Windows, or Kubernetes."""
    return SensorService.get_install_command(sensor_id=sensor_id, token="<REPLACE_WITH_ENROLLMENT_TOKEN>", os_type=os_type)


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
            sensor_type=s.sensor_type,
            sensor_version=s.sensor_version,
            status=s.status,
            health_score=s.health_score,
            offline_buffer_events=s.offline_buffer_events,
            upgrade_status=s.upgrade_status,
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
