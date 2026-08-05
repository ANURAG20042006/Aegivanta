from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.core.dependencies import require_role

router = APIRouter(prefix="/logs", tags=["Audit & Logs"])


@router.get("", summary="Get System Audit Logs")
async def get_audit_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves recent audit log events tracking logins, prediction operations, and user changes."""
    query = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource": log.resource,
            "ip_address": log.ip_address,
            "status": log.status,
            "timestamp": log.timestamp.isoformat(),
            "details": log.details
        }
        for log in logs
    ]
