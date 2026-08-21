"""
backend/app/api/v1/endpoint_xdr.py
==================================
Phase 22 Endpoint XDR & Zero-Trust Security API Router.
Exposes Normalized Telemetry, EDR Detections, XDR Multi-Domain Correlation, Zero-Trust Posture, and Containment APIs.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.services.endpoint_telemetry_service import EndpointTelemetryService
from backend.app.services.endpoint_detection_service import EndpointDetectionService
from backend.app.services.xdr_correlation_engine import XDRCorrelationEngine
from backend.app.services.zero_trust_engine import ZeroTrustEngine
from backend.app.services.endpoint_response_service import EndpointResponseService
from backend.app.observability import metrics

router = APIRouter(prefix="/endpoint-xdr", tags=["Phase 22 - Endpoint XDR & Zero-Trust"])


class IngestTelemetryRequest(BaseModel):
    sensor_id: str = Field(..., example="sensor-edr-node-01")
    hostname: str = Field(..., example="WKS-EXEC-FINANCE-04")
    event_category: str = Field(..., example="PROCESS")
    process_name: Optional[str] = None
    process_path: Optional[str] = None
    process_cmdline: Optional[str] = None
    parent_process_name: Optional[str] = None
    user_account: Optional[str] = None
    file_path: Optional[str] = None
    file_hash_sha256: Optional[str] = None
    target_ip: Optional[str] = None
    target_port: Optional[int] = None
    registry_key: Optional[str] = None
    severity: str = Field(default="INFORMATIONAL")
    raw_event: Optional[Dict[str, Any]] = None


class ZeroTrustEvaluateRequest(BaseModel):
    sensor_id: str = Field(..., example="sensor-edr-node-01")
    hostname: str = Field(..., example="WKS-EXEC-FINANCE-04")
    user_email: str = Field(..., example="jsmith@aegivanta.enterprise")
    os_patch_status: str = Field(default="UP_TO_DATE")
    edr_agent_health: str = Field(default="HEALTHY")
    disk_encryption_status: str = Field(default="ENCRYPTED_BITLOCKER")
    firewall_status: str = Field(default="ENABLED")


class ResponseActionRequest(BaseModel):
    sensor_id: str = Field(..., example="sensor-edr-node-01")
    hostname: str = Field(..., example="WKS-EXEC-FINANCE-04")
    action_type: str = Field(..., example="ISOLATE_ENDPOINT") # ISOLATE_ENDPOINT, TERMINATE_PROCESS, REVOKE_SESSION, RESET_CREDENTIALS
    target_entity: str = Field(..., example="WKS-EXEC-FINANCE-04")
    reason: str = Field(..., example="Suspected C2 beaconing and credential dump attempt")
    approval_id: Optional[str] = None


@router.get("/telemetry")
async def get_endpoint_telemetry(
    event_category: Optional[str] = None,
    hostname: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists normalized endpoint telemetry events."""
    events = await EndpointTelemetryService.list_telemetry_events(
        db=db,
        tenant_id=tenant_id,
        event_category=event_category,
        hostname=hostname,
        limit=limit
    )
    metrics.aegivanta_endpoint_telemetry_events_total.inc(len(events))
    return events


@router.post("/telemetry/ingest")
async def ingest_endpoint_telemetry(
    req: IngestTelemetryRequest,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Ingests a single endpoint telemetry event and processes detections."""
    event = await EndpointTelemetryService.ingest_event(
        db=db,
        tenant_id=tenant_id,
        sensor_id=req.sensor_id,
        hostname=req.hostname,
        event_category=req.event_category,
        process_name=req.process_name,
        process_path=req.process_path,
        process_cmdline=req.process_cmdline,
        parent_process_name=req.parent_process_name,
        user_account=req.user_account,
        file_path=req.file_path,
        file_hash_sha256=req.file_hash_sha256,
        target_ip=req.target_ip,
        target_port=req.target_port,
        registry_key=req.registry_key,
        severity=req.severity,
        raw_event=req.raw_event
    )
    # Check for EDR behavioral detections
    await EndpointDetectionService.process_and_record_detections(db, tenant_id)
    return {"status": "INGESTED", "event_id": event.id}


@router.get("/detections")
async def get_endpoint_detections(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists active EDR behavioral and threat detections."""
    dets = await EndpointDetectionService.list_detections(db=db, tenant_id=tenant_id)
    metrics.aegivanta_edr_detections_total.set(len(dets))
    return dets


@router.get("/xdr/incidents")
async def get_xdr_incidents(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists cross-domain correlated XDR incidents."""
    incidents = await XDRCorrelationEngine.list_xdr_incidents(db=db, tenant_id=tenant_id)
    metrics.aegivanta_xdr_correlated_incidents_total.set(len(incidents))
    return incidents


@router.get("/zero-trust/posture")
async def get_zero_trust_postures(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists continuous device trust postures and dynamic authorization access decisions."""
    postures = await ZeroTrustEngine.list_device_postures(db=db, tenant_id=tenant_id)
    if postures:
        avg_score = sum(p["device_trust_score"] for p in postures) / len(postures)
        metrics.aegivanta_zero_trust_device_trust_score.set(avg_score)
    return postures


@router.post("/zero-trust/evaluate")
async def evaluate_zero_trust_posture(
    req: ZeroTrustEvaluateRequest,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Evaluates zero-trust trust score and determines dynamic access decision."""
    return await ZeroTrustEngine.evaluate_and_record_posture(
        db=db,
        tenant_id=tenant_id,
        sensor_id=req.sensor_id,
        hostname=req.hostname,
        user_email=req.user_email,
        os_patch_status=req.os_patch_status,
        edr_agent_health=req.edr_agent_health,
        disk_encryption_status=req.disk_encryption_status,
        firewall_status=req.firewall_status
    )


@router.post("/response/execute")
async def execute_endpoint_response(
    req: ResponseActionRequest,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Executes a policy-controlled endpoint containment action."""
    res = await EndpointResponseService.execute_response_action(
        db=db,
        tenant_id=tenant_id,
        sensor_id=req.sensor_id,
        hostname=req.hostname,
        action_type=req.action_type,
        target_entity=req.target_entity,
        reason=req.reason,
        approval_id=req.approval_id
    )
    metrics.aegivanta_endpoint_response_actions_total.inc()
    return res


@router.post("/response/rollback/{action_id}")
async def rollback_endpoint_response(
    action_id: str,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Rolls back an executed endpoint response action."""
    return await EndpointResponseService.rollback_response_action(
        db=db,
        tenant_id=tenant_id,
        action_id=action_id
    )
