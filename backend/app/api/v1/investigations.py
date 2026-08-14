"""
backend/app/api/v1/investigations.py
====================================
Automated Incident Investigation & ATT&CK Chain Analysis Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.investigation import Investigation, InvestigationEvidence
from backend.app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/investigations", tags=["Automated Investigations & Attack Chains"])


@router.get("/{incident_id}", summary="Get Incident Investigation & Evidence Graph")
async def get_incident_investigation(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves the automated investigation summary, evidence list, and MITRE ATT&CK chain stage."""
    query = (
        select(Investigation)
        .where(Investigation.incident_id == incident_id)
        .options(selectinload(Investigation.evidence))
    )
    res = await db.execute(query)
    investigation = res.scalar_one_or_none()

    if not investigation:
        # Generate on-demand if not present
        investigation = await InvestigationService.analyze_incident(incident_id, db)
        if not investigation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")
        await db.commit()
        # Re-query with evidence loaded
        res = await db.execute(query)
        investigation = res.scalar_one_or_none()

    return {
        "id": investigation.id,
        "incident_id": investigation.incident_id,
        "asset_id": investigation.asset_id,
        "status": investigation.status,
        "summary": investigation.summary,
        "attack_chain_stage": investigation.attack_chain_stage,
        "confidence_score": investigation.confidence_score,
        "findings": investigation.findings or {},
        "recommended_actions": investigation.recommended_actions or [],
        "created_at": investigation.created_at.isoformat() if investigation.created_at else None,
        "evidence": [
            {
                "id": ev.id,
                "evidence_type": ev.evidence_type,
                "reference_id": ev.reference_id,
                "description": ev.description,
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                "metadata": ev.metadata_json or {}
            }
            for ev in (investigation.evidence or [])
        ]
    }


@router.post("/{incident_id}/run", summary="Trigger Automated Incident Investigation")
async def run_investigation(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Re-analyzes an incident, refreshes evidence links, and updates recommendations."""
    investigation = await InvestigationService.analyze_incident(incident_id, db)
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    await db.commit()
    return {
        "status": "success",
        "investigation_id": investigation.id,
        "attack_chain_stage": investigation.attack_chain_stage,
        "summary": investigation.summary
    }
