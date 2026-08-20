from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.models.alert import Alert
from backend.app.models.alert_intelligence import AlertGroup, AlertPriorityScore
from backend.app.services.alert_intelligence_service import AlertIntelligenceService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/alerts", tags=["Alert Intelligence & Prioritization"])


@router.get("/{id}/priority", summary="Get Alert Priority Score & Explainable Factor Breakdown")
async def get_alert_priority(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns normalized 0–100 priority score with explainable contributing factors."""
    stmt = select(Alert).where(Alert.id == id)
    res = await db.execute(stmt)
    alert = res.scalar_one_or_none()
    if not alert:
        raise SentinelAIException(status_code=404, detail="Alert not found.")

    score_stmt = select(AlertPriorityScore).where(AlertPriorityScore.alert_id == id)
    score_res = await db.execute(score_stmt)
    score_rec = score_res.scalar_one_or_none()

    if not score_rec:
        score_rec = await AlertIntelligenceService.calculate_priority_score(db, alert, context.tenant_id)
        await db.flush()

    return {
        "alert_id": score_rec.alert_id,
        "priority_score": score_rec.priority_score,
        "priority_level": score_rec.priority_level,
        "contributing_factors": score_rec.contributing_factors,
        "reasons": score_rec.reasons,
        "explanation": score_rec.explanation,
        "calculated_at": score_rec.calculated_at.isoformat()
    }


@router.get("/groups/active", summary="List Correlated Alert Groups")
async def list_alert_groups(
    limit: int = Query(25, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists aggregated alert groups with entity correlation context."""
    stmt = select(AlertGroup).order_by(AlertGroup.updated_at.desc()).limit(limit)
    res = await db.execute(stmt)
    groups = list(res.scalars().all())

    return [
        {
            "id": g.id,
            "group_code": g.group_code,
            "incident_id": g.incident_id,
            "title": g.title,
            "root_attack_type": g.root_attack_type,
            "alert_count": g.alert_count,
            "confidence_score": g.confidence_score,
            "status": g.status,
            "affected_assets": g.affected_assets,
            "source_ips": g.source_ips,
            "mitre_techniques": g.mitre_techniques,
            "updated_at": g.updated_at.isoformat()
        }
        for g in groups
    ]
