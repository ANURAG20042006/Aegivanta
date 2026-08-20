"""
backend/app/api/v1/investigations.py
====================================
Phase 3.8 SOC Investigation Cases, Evidence Graphs, Pivots, and Timelines.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.investigation import InvestigationCase, InvestigationEvidence, InvestigationNote, InvestigationTimeline, Investigation
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.services.investigation_case_service import InvestigationCaseService
from backend.app.services.evidence_correlation_service import EvidenceCorrelationEngine
from backend.app.services.investigation_pivot_service import InvestigationPivotService
from backend.app.services.mitre_coverage_service import MitreCoverageService
from backend.app.services.risk_scoring_service import RiskScoringService
from backend.app.services.threat_graph_service import ThreatGraphService
from backend.app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/investigations", tags=["SOC Investigation Cases & Evidence Engine"])


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CreateCaseRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="HIGH")
    severity: str = Field(default="HIGH")
    analyst: str = Field(default="unassigned")
    linked_incident_ids: List[str] = Field(default_factory=list)
    linked_assets: List[str] = Field(default_factory=list)
    linked_users: List[str] = Field(default_factory=list)
    linked_iocs: List[str] = Field(default_factory=list)
    mitre_techniques: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    risk_score: float = Field(default=50.0, ge=0.0, le=100.0)


class UpdateCaseRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    analyst: Optional[str] = None
    tags: Optional[List[str]] = None


class AddEvidenceRequest(BaseModel):
    evidence_type: str = Field(..., description="ALERT, FLOW_TELEMETRY, IOC_MATCH, BEHAVIORAL_ANOMALY, PIVOT, LOG")
    reference_id: Optional[str] = None
    description: str = Field(..., min_length=3)
    metadata_json: Optional[Dict[str, Any]] = None


class AddNoteRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class PivotRequest(BaseModel):
    entity_type: str = Field(..., description="IP, USER, ASSET, IOC, INCIDENT")
    entity_value: str = Field(..., min_length=1)
    limit: int = Field(default=50, ge=1, le=200)


class CloseCaseRequest(BaseModel):
    resolution_summary: str = Field(..., min_length=5, max_length=2000)


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("/statistics", summary="Get Investigation Cases Statistics")
async def get_investigation_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns aggregated metrics on active cases, priorities, and statuses."""
    return await InvestigationCaseService.get_statistics(db=db)


@router.post("", summary="Create New Investigation Case", status_code=status.HTTP_201_CREATED)
async def create_investigation_case(
    payload: CreateCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Initializes a new SOC investigation case."""
    case = await InvestigationCaseService.create_case(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        severity=payload.severity,
        analyst=payload.analyst if payload.analyst != "unassigned" else current_user.username,
        linked_incident_ids=payload.linked_incident_ids,
        linked_assets=payload.linked_assets,
        linked_users=payload.linked_users,
        linked_iocs=payload.linked_iocs,
        mitre_techniques=payload.mitre_techniques,
        tags=payload.tags,
        risk_score=payload.risk_score,
        db=db
    )
    return {
        "id": case.id,
        "case_code": case.case_code,
        "title": case.title,
        "status": case.status,
        "priority": case.priority,
        "severity": case.severity,
        "analyst": case.analyst,
        "risk_score": case.risk_score,
        "created_at": case.created_at.isoformat()
    }


@router.get("", summary="List Investigation Cases with Pagination & Filters")
async def list_investigation_cases(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    severity_filter: Optional[str] = Query(None, alias="severity"),
    analyst_filter: Optional[str] = Query(None, alias="analyst"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists investigation cases matching specified criteria."""
    cases = await InvestigationCaseService.list_cases(
        status_filter=status_filter,
        priority_filter=priority_filter,
        severity_filter=severity_filter,
        analyst_filter=analyst_filter,
        limit=limit,
        offset=offset,
        db=db
    )
    return [
        {
            "id": c.id,
            "case_code": c.case_code,
            "title": c.title,
            "description": c.description,
            "status": c.status,
            "priority": c.priority,
            "severity": c.severity,
            "analyst": c.analyst,
            "linked_incident_ids": c.linked_incident_ids,
            "linked_assets": c.linked_assets,
            "linked_users": c.linked_users,
            "linked_iocs": c.linked_iocs,
            "mitre_techniques": c.mitre_techniques,
            "tags": c.tags,
            "risk_score": c.risk_score,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat()
        }
        for c in cases
    ]


@router.get("/{case_id}", summary="Get Detailed Investigation Case Record")
async def get_investigation_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves full case details including evidence items, timeline events, and notes."""
    case = await InvestigationCaseService.get_case(case_id, db)
    if not case:
        # Check if legacy incident investigation exists or generate on demand
        legacy_inv = await db.execute(
            select(Investigation)
            .where(Investigation.incident_id == case_id)
            .options(selectinload(Investigation.evidence))
        )
        inv = legacy_inv.scalar_one_or_none()
        if not inv:
            inv = await InvestigationService.analyze_incident(case_id, db)
            if inv:
                await db.commit()
                legacy_inv = await db.execute(
                    select(Investigation)
                    .where(Investigation.incident_id == case_id)
                    .options(selectinload(Investigation.evidence))
                )
                inv = legacy_inv.scalar_one_or_none()

        if inv:
            return {
                "id": inv.id,
                "incident_id": inv.incident_id,
                "asset_id": inv.asset_id,
                "status": inv.status,
                "summary": inv.summary,
                "attack_chain_stage": inv.attack_chain_stage,
                "confidence_score": inv.confidence_score,
                "findings": inv.findings or {},
                "recommended_actions": inv.recommended_actions or [
                    "Isolate source host",
                    "Block attacker IP",
                    "Rotate exposed credentials"
                ],
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "evidence": [
                    {
                        "id": ev.id,
                        "evidence_type": ev.evidence_type,
                        "reference_id": ev.reference_id,
                        "description": ev.description,
                        "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                        "metadata": ev.metadata_json or {}
                    }
                    for ev in (inv.evidence or [])
                ]
            }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation case not found.")

    return {
        "id": case.id,
        "case_code": case.case_code,
        "title": case.title,
        "description": case.description,
        "status": case.status,
        "priority": case.priority,
        "severity": case.severity,
        "analyst": case.analyst,
        "linked_incident_ids": case.linked_incident_ids,
        "linked_assets": case.linked_assets,
        "linked_users": case.linked_users,
        "linked_iocs": case.linked_iocs,
        "mitre_techniques": case.mitre_techniques,
        "tags": case.tags,
        "risk_score": case.risk_score,
        "recommended_actions": [f"Review telemetry for {case.title}"],
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
        "closed_at": case.closed_at.isoformat() if case.closed_at else None,
        "notes": [
            {"id": n.id, "author": n.author, "content": n.content, "created_at": n.created_at.isoformat()}
            for n in case.notes
        ],
        "evidence": [
            {"id": e.id, "evidence_type": e.evidence_type, "reference_id": e.reference_id, "description": e.description, "metadata": e.metadata_json}
            for e in case.evidence_items
        ]
    }


@router.patch("/{case_id}", summary="Update Investigation Case Status and Metadata")
async def update_investigation_case(
    case_id: str,
    payload: UpdateCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Updates status, priority, severity, or assigned analyst for an active case."""
    try:
        case = await InvestigationCaseService.update_case(
            case_id=case_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            severity=payload.severity,
            status=payload.status,
            analyst=payload.analyst,
            tags=payload.tags,
            actor=current_user.username,
            db=db
        )
        return {
            "status": "SUCCESS",
            "id": case.id,
            "case_code": case.case_code,
            "current_status": case.status,
            "priority": case.priority,
            "analyst": case.analyst
        }
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{case_id}/evidence", summary="Add Evidence Item to Case", status_code=status.HTTP_201_CREATED)
async def add_case_evidence(
    case_id: str,
    payload: AddEvidenceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Attaches a verified forensic evidence item to the investigation case."""
    try:
        ev = await InvestigationCaseService.add_evidence(
            case_id=case_id,
            evidence_type=payload.evidence_type,
            reference_id=payload.reference_id,
            description=payload.description,
            metadata_json=payload.metadata_json,
            actor=current_user.username,
            db=db
        )
        return {
            "status": "SUCCESS",
            "evidence_id": ev.id,
            "case_id": ev.case_id,
            "evidence_type": ev.evidence_type,
            "description": ev.description
        }
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{case_id}/evidence", summary="List All Evidence Items for Case")
async def list_case_evidence(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves all evidence records associated with an investigation case."""
    case = await InvestigationCaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation case not found.")

    return [
        {
            "id": e.id,
            "evidence_type": e.evidence_type,
            "reference_id": e.reference_id,
            "description": e.description,
            "metadata": e.metadata_json,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None
        }
        for e in case.evidence_items
    ]


@router.post("/{case_id}/pivot", summary="Execute Entity Pivot Search for Case")
async def pivot_case_entity(
    case_id: str,
    payload: PivotRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Executes multi-entity pivot search on given IP, user, asset, or IOC seed."""
    case = await InvestigationCaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation case not found.")

    return await InvestigationPivotService.pivot_entity(
        entity_type=payload.entity_type,
        entity_value=payload.entity_value,
        limit=payload.limit,
        db=db
    )


@router.get("/{case_id}/timeline", summary="Get Chronological Investigation Timeline")
async def get_case_timeline(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Reconstructs ordered chronological timeline of events for the case."""
    case = await InvestigationCaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation case not found.")

    return [
        {
            "id": t.id,
            "event_type": t.event_type,
            "title": t.title,
            "description": t.description,
            "actor": t.actor,
            "metadata": t.metadata_json,
            "timestamp": t.timestamp.isoformat()
        }
        for t in sorted(case.timeline_events, key=lambda x: x.timestamp)
    ]


@router.get("/{case_id}/graph", summary="Get Correlated Evidence Graph for Case")
async def get_case_evidence_graph(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns nodes and directed edges forming the complete evidence relationship graph."""
    case = await InvestigationCaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation case not found.")

    return await EvidenceCorrelationEngine.correlate_case_evidence(
        incident_ids=case.linked_incident_ids,
        ips=case.linked_assets,
        users=case.linked_users,
        assets=case.linked_assets,
        iocs=case.linked_iocs,
        db=db
    )


@router.get("/{case_id}/risk", summary="Get Explainable Case Risk Breakdown")
async def get_case_risk_breakdown(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns explainable multi-signal risk contribution breakdown."""
    case = await InvestigationCaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation case not found.")

    risk_eval = RiskScoringService.calculate_risk_score(
        base_severity=case.severity,
        confidence=0.90,
        matched_iocs_count=len(case.linked_iocs or []),
        has_lateral_movement=len(case.linked_assets or []) > 1,
        crown_jewel_impact=50.0 if case.severity == "CRITICAL" else 20.0
    )
    return {
        "case_id": case.id,
        "case_code": case.case_code,
        "total_risk_score": risk_eval["risk_score"],
        "risk_level": risk_eval["risk_level"],
        "components": risk_eval["components"]
    }


@router.get("/{case_id}/mitre", summary="Get MITRE ATT&CK Technique Coverage for Case")
async def get_case_mitre_coverage(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns MITRE ATT&CK techniques mapped to this investigation case."""
    case = await InvestigationCaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation case not found.")

    coverage = MitreCoverageService.get_coverage_summary()
    return {
        "case_id": case.id,
        "mapped_techniques": case.mitre_techniques or [],
        "matrix_coverage": coverage
    }


@router.post("/{case_id}/notes", summary="Add Analyst Forensic Note", status_code=status.HTTP_201_CREATED)
async def add_case_note(
    case_id: str,
    payload: AddNoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Adds an analyst note to the case record."""
    try:
        note = await InvestigationCaseService.add_note(
            case_id=case_id,
            author=current_user.username,
            content=payload.content,
            db=db
        )
        return {
            "status": "SUCCESS",
            "note_id": note.id,
            "case_id": note.case_id,
            "author": note.author,
            "created_at": note.created_at.isoformat()
        }
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{case_id}/close", summary="Formally Close Investigation Case")
async def close_case_endpoint(
    case_id: str,
    payload: CloseCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Resolves and formally closes an active investigation case."""
    try:
        case = await InvestigationCaseService.close_case(
            case_id=case_id,
            closed_by=current_user.username,
            resolution_summary=payload.resolution_summary,
            db=db
        )
        return {
            "status": "SUCCESS",
            "case_id": case.id,
            "case_code": case.case_code,
            "current_status": case.status,
            "closed_at": case.closed_at.isoformat() if case.closed_at else None
        }
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
