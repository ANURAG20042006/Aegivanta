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


from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.alert import Alert
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.schemas.incident_extended import TimelineEventCreate
from backend.app.api.v1.websockets import manager


@router.get("", summary="Search and Paginate Recorded Incidents")
async def list_incidents(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    severity: Optional[str] = Query(default=None, min_length=1, max_length=15),
    is_malicious: Optional[bool] = None,
    attack_type: Optional[str] = Query(default=None, min_length=1, max_length=50),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    asset_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns real incident records with server-side filters for analyst workflows."""
    filters = []
    if severity:
        filters.append(Incident.severity == severity.capitalize())
    if is_malicious is not None:
        filters.append(Incident.is_malicious == is_malicious)
    if attack_type:
        filters.append(Incident.attack_type == attack_type)
    if status_filter:
        filters.append(Incident.status == status_filter.upper())
    if asset_id:
        filters.append(Incident.asset_id == asset_id)

    total = (await db.execute(select(func.count(Incident.id)).where(*filters))).scalar_one()
    result = await db.execute(
        select(Incident)
        .where(*filters)
        .order_by(Incident.risk_score.desc(), Incident.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    items = [
        {
            "id": incident.id,
            "incident_code": incident.incident_code,
            "alert_id": incident.alert_id,
            "asset_id": incident.asset_id,
            "title": incident.title or f"Incident: {incident.attack_type}",
            "description": incident.description,
            "status": incident.status,
            "risk_score": incident.risk_score,
            "alert_count": incident.alert_count,
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
            "resolution": incident.resolution,
            "remediation_action": incident.remediation_action,
            "timestamp": incident.timestamp.isoformat(),
            "first_seen": (incident.first_seen or incident.timestamp).isoformat(),
            "last_seen": (incident.last_seen or incident.timestamp).isoformat(),
            "triaged_at": incident.triaged_at.isoformat() if incident.triaged_at else None,
            "closed_at": incident.closed_at.isoformat() if incident.closed_at else None
        }
        for incident in result.scalars().all()
    ]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{incident_id}", summary="Get Incident Details with Timeline & Correlated Alerts")
async def get_incident_details(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves full details of a specific security incident including associated alerts and attack timeline."""
    query = select(Incident).where(
        (Incident.id == incident_id) | 
        (Incident.alert_id == incident_id) | 
        (Incident.incident_code == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    # Fetch associated alerts
    alerts_query = select(Alert).where(Alert.incident_id == incident.id).order_by(Alert.timestamp.asc())
    alerts_res = await db.execute(alerts_query)
    alerts_list = alerts_res.scalars().all()

    # Fetch chronological timeline
    timeline_query = select(IncidentTimelineEvent).where(
        IncidentTimelineEvent.incident_id == incident.id
    ).order_by(IncidentTimelineEvent.timestamp.asc())
    timeline_res = await db.execute(timeline_query)
    timeline_list = timeline_res.scalars().all()

    # Fetch associated asset if any
    asset_data = None
    if incident.asset_id:
        asset_stmt = select(ProtectedAsset).where(ProtectedAsset.id == incident.asset_id)
        asset_obj = (await db.execute(asset_stmt)).scalar_one_or_none()
        if asset_obj:
            asset_data = {
                "id": asset_obj.id,
                "name": asset_obj.name,
                "hostname": asset_obj.hostname,
                "url": asset_obj.url,
                "ip_address": asset_obj.ip_address,
                "asset_type": asset_obj.asset_type,
                "environment": asset_obj.environment,
                "criticality": asset_obj.criticality,
                "status": asset_obj.status,
                "risk_score": asset_obj.risk_score,
                "last_seen": asset_obj.last_seen.isoformat()
            }

    return {
        "id": incident.id,
        "incident_code": incident.incident_code,
        "alert_id": incident.alert_id,
        "asset_id": incident.asset_id,
        "title": incident.title or f"Incident: {incident.attack_type}",
        "description": incident.description,
        "status": incident.status,
        "risk_score": incident.risk_score,
        "alert_count": incident.alert_count,
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
        "resolution": incident.resolution,
        "remediation_action": incident.remediation_action,
        "timestamp": incident.timestamp.isoformat(),
        "first_seen": (incident.first_seen or incident.timestamp).isoformat(),
        "last_seen": (incident.last_seen or incident.timestamp).isoformat(),
        "triaged_at": incident.triaged_at.isoformat() if incident.triaged_at else None,
        "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
        "feature_payload": incident.feature_payload,
        "asset": asset_data,
        "alerts": [
            {
                "id": a.id,
                "alert_id": a.alert_id,
                "title": a.title,
                "severity": a.severity,
                "confidence": a.confidence,
                "risk_score": a.risk_score,
                "attack_type": a.attack_type,
                "source_ip": a.source_ip,
                "destination_ip": a.destination_ip,
                "status": a.status,
                "explanation": a.explanation,
                "timestamp": a.timestamp.isoformat()
            } for a in alerts_list
        ],
        "timeline": [
            {
                "id": t.id,
                "timestamp": t.timestamp.isoformat(),
                "event_type": t.event_type,
                "title": t.title,
                "description": t.description,
                "actor": t.actor,
                "metadata_payload": t.metadata_payload
            } for t in timeline_list
        ]
    }


@router.post("/{incident_id}/timeline", summary="Add Analyst Note / Custom Timeline Event")
async def add_incident_timeline_event(
    incident_id: str,
    payload: TimelineEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Appends an analyst investigation note to the chronological attack timeline."""
    query = select(Incident).where(
        (Incident.id == incident_id) | 
        (Incident.alert_id == incident_id) | 
        (Incident.incident_code == incident_id)
    )
    incident = (await db.execute(query)).scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    timeline_event = IncidentTimelineEvent(
        incident_id=incident.id,
        timestamp=datetime.now(timezone.utc),
        event_type=payload.event_type,
        title=payload.title,
        description=payload.description,
        actor=current_user.username,
        metadata_payload=payload.metadata_payload
    )
    db.add(timeline_event)
    await db.commit()
    await db.refresh(timeline_event)

    return {
        "status": "SUCCESS",
        "event_id": timeline_event.id,
        "incident_id": incident.id,
        "title": timeline_event.title,
        "actor": timeline_event.actor,
        "timestamp": timeline_event.timestamp.isoformat()
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
    Validates state machine transition matrix and appends to attack timeline.
    """
    new_status = payload.status.upper()
    if new_status not in VALID_INCIDENT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Valid choices: {VALID_INCIDENT_STATUSES}"
        )

    query = select(Incident).where(
        (Incident.id == incident_id) | 
        (Incident.alert_id == incident_id) | 
        (Incident.incident_code == incident_id)
    )
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

    old_status = incident.status
    incident.status = new_status
    incident.analyst = current_user.username
    if payload.notes:
        incident.notes = payload.notes

    if new_status == "TRIAGED" and not incident.triaged_at:
        incident.triaged_at = datetime.now(timezone.utc)
    elif new_status == "CLOSED":
        incident.closed_at = datetime.now(timezone.utc)

    # Add timeline event for status transition
    timeline_event = IncidentTimelineEvent(
        incident_id=incident.id,
        timestamp=datetime.now(timezone.utc),
        event_type="STATUS_CHANGE",
        title=f"Incident Status: {new_status}",
        description=f"Status transitioned from {old_status} to {new_status} by @{current_user.username}. Notes: {payload.notes or 'None'}",
        actor=current_user.username
    )
    db.add(timeline_event)

    audit = AuditLog(
        user_id=current_user.id,
        action=f"INCIDENT_STATUS_{new_status}",
        resource="INCIDENTS",
        details={"message": f"Incident '{incident.incident_code}' changed from {old_status} to {new_status}. Notes: {payload.notes or 'None'}"}
    )
    db.add(audit)
    await db.commit()

    # Broadcast WebSocket update
    try:
        await manager.broadcast_event("INCIDENT_STATUS_CHANGE", {
            "incident_id": incident.id,
            "incident_code": incident.incident_code,
            "old_status": old_status,
            "new_status": new_status,
            "analyst": current_user.username,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception:
        pass

    return {
        "status": "SUCCESS",
        "incident_id": incident.id,
        "incident_code": incident.incident_code,
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
    Appends remediation step to attack timeline and logs audit trail.
    """
    query = select(Incident).where(
        (Incident.id == incident_id) | 
        (Incident.alert_id == incident_id) | 
        (Incident.incident_code == incident_id)
    )
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

    # Add timeline event
    timeline_event = IncidentTimelineEvent(
        incident_id=incident.id,
        timestamp=datetime.now(timezone.utc),
        event_type="REMEDIATION",
        title=f"Remediation Executed: {payload.action}",
        description=f"Action '{payload.action}' executed on source IP {incident.source_ip}. Mode: {mode_label}. Reason: {payload.reason or 'Threat containment'}",
        actor=current_user.username
    )
    db.add(timeline_event)

    audit = AuditLog(
        user_id=current_user.id,
        action="INCIDENT_REMEDIATION_EXECUTED",
        resource="INCIDENTS",
        details={"message": f"Remediation '{payload.action}' on incident '{incident.incident_code}' targeting IP {incident.source_ip}."}
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "SUCCESS",
        "mode": mode_label,
        "incident_id": incident.id,
        "incident_code": incident.incident_code,
        "remediation_action": remediation_str,
        "current_status": incident.status,
        "executed_by": current_user.username
    }
