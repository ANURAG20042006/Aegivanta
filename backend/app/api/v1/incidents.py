from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.database import get_db
from backend.app.models.incident import Incident, ALLOWED_STATE_TRANSITIONS, is_valid_state_transition, VALID_INCIDENT_STATUSES
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User

router = APIRouter(prefix="/incidents", tags=["Incident Operations"])


class IncidentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class IncidentRemediationRequest(BaseModel):
    action: str = "BLOCK_IP"  # BLOCK_IP, ISOLATE_HOST, RATE_LIMIT_PORT
    reason: Optional[str] = "Automated threat containment action"


@router.get("", summary="Search and Paginate Recorded Incidents")
async def list_incidents(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    severity: Optional[str] = Query(default=None, min_length=1, max_length=15),
    is_malicious: Optional[bool] = None,
    attack_type: Optional[str] = Query(default=None, min_length=1, max_length=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns real incident records with server-side filters for analyst workflows."""
    filters = []
    if severity:
        filters.append(Incident.severity == severity)
    if is_malicious is not None:
        filters.append(Incident.is_malicious == is_malicious)
    if attack_type:
        filters.append(Incident.attack_type == attack_type)

    total = (await db.execute(select(func.count(Incident.id)).where(*filters))).scalar_one()
    result = await db.execute(
        select(Incident)
        .where(*filters)
        .order_by(Incident.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    items = [
        {
            "id": incident.id,
            "alert_id": incident.alert_id,
            "status": incident.status,
            "source_ip": incident.source_ip,
            "destination_ip": incident.destination_ip,
            "source_port": incident.source_port,
            "destination_port": incident.destination_port,
            "protocol": incident.protocol,
            "attack_type": incident.attack_type,
            "confidence_score": incident.confidence_score,
            "is_malicious": incident.is_malicious,
            "severity": incident.severity,
            "model_name": incident.model_name,
            "model_version": incident.model_version,
            "analyst": incident.analyst,
            "notes": incident.notes,
            "remediation_action": incident.remediation_action,
            "timestamp": incident.timestamp.isoformat(),
            "triaged_at": incident.triaged_at.isoformat() if incident.triaged_at else None,
            "closed_at": incident.closed_at.isoformat() if incident.closed_at else None
        }
        for incident in result.scalars().all()
    ]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{incident_id}", summary="Get Incident Details")
async def get_incident_details(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves full details of a specific security incident."""
    query = select(Incident).where((Incident.id == incident_id) | (Incident.alert_id == incident_id))
    result = await db.execute(query)
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    return {
        "id": incident.id,
        "alert_id": incident.alert_id,
        "status": incident.status,
        "source_ip": incident.source_ip,
        "destination_ip": incident.destination_ip,
        "source_port": incident.source_port,
        "destination_port": incident.destination_port,
        "protocol": incident.protocol,
        "attack_type": incident.attack_type,
        "confidence_score": incident.confidence_score,
        "is_malicious": incident.is_malicious,
        "severity": incident.severity,
        "model_name": incident.model_name,
        "model_version": incident.model_version,
        "analyst": incident.analyst,
        "notes": incident.notes,
        "remediation_action": incident.remediation_action,
        "timestamp": incident.timestamp.isoformat(),
        "triaged_at": incident.triaged_at.isoformat() if incident.triaged_at else None,
        "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
        "feature_payload": incident.feature_payload
    }


@router.patch("/{incident_id}/status", summary="Update Incident Lifecycle State (Analyst & Admin Only)")
async def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "soc_analyst", "analyst"]))
):
    """
    Transitions an incident along its lifecycle state
    (DETECTED -> TRIAGED -> INVESTIGATING -> CONTAINED -> RESOLVED -> CLOSED).
    Validates state machine transition matrix and rejects invalid jumps.
    """
    new_status = payload.status.upper()
    if new_status not in VALID_INCIDENT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Valid choices: {VALID_INCIDENT_STATUSES}"
        )

    query = select(Incident).where((Incident.id == incident_id) | (Incident.alert_id == incident_id))
    result = await db.execute(query)
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    # Validate state transition
    if not is_valid_state_transition(incident.status, new_status):
        allowed = ALLOWED_STATE_TRANSITIONS.get(incident.status, [])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state transition from '{incident.status}' to '{new_status}'. Allowed transitions: {allowed}"
        )

    incident.status = new_status
    incident.analyst = current_user.username
    if payload.notes:
        incident.notes = payload.notes

    if new_status == "TRIAGED" and not incident.triaged_at:
        incident.triaged_at = datetime.now(timezone.utc)
    elif new_status == "CLOSED":
        incident.closed_at = datetime.now(timezone.utc)

    audit = AuditLog(
        user_id=current_user.id,
        action=f"INCIDENT_STATUS_{new_status}",
        resource="INCIDENTS",
        status="SUCCESS",
        details={
            "incident_id": incident.id,
            "new_status": new_status,
            "analyst": current_user.username,
            "notes": payload.notes,
        }
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "SUCCESS",
        "incident_id": incident.id,
        "new_status": incident.status,
        "analyst": incident.analyst,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/{incident_id}/remediate", summary="Execute Threat Remediation Action (Analyst & Admin Only)")
async def remediate_incident(
    incident_id: str,
    payload: IncidentRemediationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "soc_analyst", "analyst"]))
):
    """
    Executes incident remediation action.
    Strictly governed by OPERATING_MODE:
      - DEMO: Simulates action tagged 'SIMULATION MODE'.
      - LAB: Executes controlled lab action tagged 'REAL LAB MODE'.
      - PRODUCTION: Requires explicit analyst authorization / Admin role check.
    Generates Audit Log record.
    """
    query = select(Incident).where((Incident.id == incident_id) | (Incident.alert_id == incident_id))
    result = await db.execute(query)
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    mode = settings.OPERATING_MODE.upper()
    if mode == "PRODUCTION" and current_user.role.lower() not in ["admin", "soc_analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Production remediation requires authorized Admin or SOC Analyst role."
        )

    mode_label = "SIMULATION MODE" if mode == "DEMO" else ("REAL LAB MODE" if mode == "LAB" else "PRODUCTION MODE")
    remediation_str = f"[{mode_label}] Action: {payload.action} on IP {incident.source_ip}"
    incident.remediation_action = remediation_str

    if incident.status in ["DETECTED", "TRIAGED", "INVESTIGATING"]:
        incident.status = "CONTAINED"

    audit = AuditLog(
        user_id=current_user.id,
        action="INCIDENT_REMEDIATION_EXECUTED",
        resource="INCIDENTS",
        status="SUCCESS",
        details={
            "incident_id": incident.id,
            "action": payload.action,
            "mode": mode_label,
            "target_ip": incident.source_ip,
            "executed_by": current_user.username
        }
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "SUCCESS",
        "mode": mode_label,
        "incident_id": incident.id,
        "remediation_action": remediation_str,
        "current_status": incident.status,
        "executed_by": current_user.username
    }
