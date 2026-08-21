"""
backend/app/api/v1/executive_security_intelligence.py
======================================================
Phase 47 — Executive Security Intelligence, Cyber ROI & CISO Posture Reporting Router.
Exposes:
- Executive Intelligence Posture Scorecard
- CISO Board Report Generation & Management
- Cyber ROI Financial Metrics
- Executive KPI Snapshots (Weekly)
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.ciso_report_service import CISOReportService
from backend.app.services.cyber_roi_service import CyberROIService
from backend.app.services.executive_intelligence_posture_service import ExecutiveIntelligencePostureService

router = APIRouter(
    prefix="/executive-intelligence",
    tags=["Phase 47 - Executive Security Intelligence"]
)


# ==================== Request Payloads ====================

class GenerateReportRequest(BaseModel):
    report_period: str = Field(..., example="Q3-2026")
    report_type: str = Field(default="ON_DEMAND", example="ON_DEMAND")


# ==================== Endpoints ====================

@router.get(
    "/summary",
    summary="Executive Intelligence Posture Scorecard",
    description=(
        "Returns the consolidated executive security intelligence scorecard including "
        "current security score, ROI metrics, automation coverage, and CISO priorities."
    )
)
async def get_executive_posture_summary(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await ExecutiveIntelligencePostureService.get_posture_summary(
        db=db, tenant_id=ctx.tenant_id
    )


@router.get(
    "/reports",
    summary="List CISO Board Reports",
    description="Lists all generated CISO board posture reports, most recent first."
)
async def list_ciso_reports(
    limit: int = Query(default=20, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await CISOReportService.list_reports(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.get(
    "/reports/latest",
    summary="Get Latest CISO Board Report",
    description="Returns the most recently generated CISO board posture report."
)
async def get_latest_ciso_report(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await CISOReportService.get_latest_report(db=db, tenant_id=ctx.tenant_id)


@router.post(
    "/reports/generate",
    summary="Generate On-Demand CISO Board Report",
    description=(
        "Generates a new on-demand CISO board report for the specified reporting period. "
        "Calculates live security score, ROI metrics, and compliance posture."
    )
)
async def generate_ciso_report(
    payload: GenerateReportRequest = Body(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await CISOReportService.generate_report(
        db=db,
        tenant_id=ctx.tenant_id,
        report_period=payload.report_period,
        report_type=payload.report_type
    )


@router.get(
    "/roi",
    summary="Cyber ROI Financial Metrics",
    description=(
        "Returns historical Cyber ROI records including security investment, "
        "losses prevented, breach probability reduction, and automation labor savings."
    )
)
async def list_cyber_roi(
    limit: int = Query(default=20, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await CyberROIService.list_roi_records(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.get(
    "/roi/latest",
    summary="Latest Cyber ROI Record",
    description="Returns the most recent Cyber ROI financial metrics record."
)
async def get_latest_roi(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await CyberROIService.get_latest_roi(db=db, tenant_id=ctx.tenant_id)


@router.get(
    "/kpi-snapshots",
    summary="Weekly Executive KPI Snapshots",
    description=(
        "Returns weekly executive KPI snapshots covering threats blocked, MTTR, "
        "SLA compliance, automation coverage, and compliance framework status."
    )
)
async def list_kpi_snapshots(
    limit: int = Query(default=20, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await ExecutiveIntelligencePostureService.list_kpi_snapshots(
        db=db, tenant_id=ctx.tenant_id, limit=limit
    )
