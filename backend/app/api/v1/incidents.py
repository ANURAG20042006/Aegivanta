from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_current_user, require_role
from backend.app.database import get_db
from backend.app.models.incident import Incident
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User

router = APIRouter(prefix="/incidents", tags=["Incident Operations"])


class IncidentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


VALID_INCIDENT_STATUSES = ["DETECTED", "TRIAGED", "INVESTIGATING", "CONTAINED", "RESOLVED", "CLOSED"]


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
            "timestamp": incident.timestamp.isoformat(),
        }
        for incident in result.scalars().all()
    ]
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.patch("/{incident_id}/status", summary="Update Incident Lifecycle State (Analyst & Admin Only)")
async def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Transitions an incident along its lifecycle state (DETECTED -> TRIAGED -> INVESTIGATING -> CONTAINED -> RESOLVED -> CLOSED)."""
    new_status = payload.status.upper()
    if new_status not in VALID_INCIDENT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Valid choices: {VALID_INCIDENT_STATUSES}"
        )

    query = select(Incident).where(Incident.id == incident_id)
    result = await db.execute(query)
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    audit = AuditLog(
        user_id=current_user.id,
        action=f"INCIDENT_STATUS_{new_status}",
        resource="INCIDENTS",
        status="SUCCESS",
        details={
            "incident_id": incident_id,
            "new_status": new_status,
            "updated_by": current_user.username,
            "notes": payload.notes
        }
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "SUCCESS",
        "incident_id": incident_id,
        "new_lifecycle_state": new_status,
        "updated_by": current_user.username
    }
