from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_current_user
from backend.app.database import get_db
from backend.app.models.incident import Incident
from backend.app.models.user import User


router = APIRouter(prefix="/incidents", tags=["Incident Operations"])


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
