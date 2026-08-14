"""
backend/app/api/v1/attack_coverage.py
=====================================
API Endpoints for MITRE ATT&CK Matrix Coverage Analytics.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.services.attack_coverage_service import AttackCoverageService

router = APIRouter(prefix="/attack-coverage", tags=["MITRE ATT&CK Coverage Analytics"])


@router.get("", summary="Get MITRE ATT&CK Coverage Matrix")
async def get_attack_coverage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns the latest empirical ATT&CK matrix visibility snapshot."""
    snapshot = await AttackCoverageService.get_latest_coverage(db)
    return {
        "id": snapshot.id,
        "observed_techniques_count": snapshot.observed_techniques_count,
        "detected_techniques_count": snapshot.detected_techniques_count,
        "total_matrix_techniques": snapshot.total_matrix_techniques,
        "coverage_percentage": snapshot.coverage_percentage,
        "tactic_breakdown": snapshot.tactic_breakdown,
        "technique_details": snapshot.technique_details,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None
    }


@router.post("/snapshot", summary="Recompute ATT&CK Coverage Snapshot", status_code=status.HTTP_201_CREATED)
async def recompute_coverage_snapshot(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Recomputes the ATT&CK coverage snapshot against active detections."""
    snapshot = await AttackCoverageService.compute_coverage_snapshot(db)
    return {
        "id": snapshot.id,
        "coverage_percentage": snapshot.coverage_percentage,
        "detected_techniques_count": snapshot.detected_techniques_count,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None
    }
