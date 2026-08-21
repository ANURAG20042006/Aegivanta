"""
backend/app/api/v1/soc_cases.py
===============================
Phase 26.6 & 26.7 Enterprise SOC Case Management & Forensic Evidence APIs.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.soc_case_management_service import SOCCaseManagementService
from backend.app.services.evidence_custody_service import EvidenceCustodyService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/soc", tags=["Enterprise SOC Case Management & Evidence"])


class CreateCaseRequest(BaseModel):
    title: str = Field(..., example="Lateral Movement Investigation")
    description: str = Field(..., example="Correlated anomalous SMB probes across internal workstations.")
    priority: str = Field(default="HIGH", example="HIGH")
    severity: str = Field(default="HIGH", example="HIGH")
    lead_analyst_id: Optional[str] = Field(default=None, example="analyst@aegivanta.io")
    affected_assets: List[str] = Field(default_factory=list, example=["WKS-EXEC-01"])
    affected_identities: List[str] = Field(default_factory=list, example=["alice.smith"])
    mitre_attack_techniques: List[str] = Field(default_factory=list, example=["T1059.001", "T1021.002"])
    sla_target_hours: float = Field(default=4.0)
    risk_score: float = Field(default=75.0)


class UpdateCaseStatusRequest(BaseModel):
    status: str = Field(..., example="INVESTIGATING")


class AddCommentRequest(BaseModel):
    author: str = Field(default="ANALYST", example="analyst@aegivanta.io")
    comment_text: str = Field(..., example="Extracted memory dump and confirmed presence of injected payload.")
    is_internal: bool = Field(default=True)


class AddTaskRequest(BaseModel):
    title: str = Field(..., example="Quarantine compromised workstation")
    description: Optional[str] = None
    assigned_to: Optional[str] = None


class RegisterEvidenceRequest(BaseModel):
    title: str = Field(..., example="Process Execution Memory Dump")
    description: str = Field(..., example="Raw memory extract of powershell.exe process PID 4820")
    evidence_type: str = Field(..., example="PROCESS_EVENT")
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
    source_system: str = Field(default="aegivanta.edr")
    collected_by: str = Field(default="ANALYST")


class TransferCustodyRequest(BaseModel):
    source_custodian: str = Field(..., example="SOC Tier 1")
    target_custodian: str = Field(..., example="Incident Commander")
    action: str = Field(default="TRANSFERRED")
    notes: Optional[str] = None


# ==================== Case Management Endpoints ====================

@router.get("/cases", summary="List SOC Cases")
async def list_cases(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists all SOC investigation cases for the tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    cases = await SOCCaseManagementService.list_cases(
        db=db,
        tenant_id=tenant_id,
        status_filter=status,
        priority_filter=priority,
        limit=limit
    )
    return [
        {
            "id": c.id,
            "case_number": c.case_number,
            "title": c.title,
            "description": c.description,
            "status": c.status,
            "priority": c.priority,
            "severity": c.severity,
            "lead_analyst_id": c.lead_analyst_id,
            "risk_score": c.risk_score,
            "affected_assets": c.affected_assets,
            "affected_identities": c.affected_identities,
            "is_sla_breached": c.is_sla_breached,
            "created_at": c.created_at.isoformat()
        }
        for c in cases
    ]


@router.post("/cases", summary="Create New SOC Case")
async def create_case(
    req: CreateCaseRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new SOC investigation case."""
    tenant_id = context.tenant_id or "default-tenant"
    case = await SOCCaseManagementService.create_case(
        db=db,
        tenant_id=tenant_id,
        title=req.title,
        description=req.description,
        priority=req.priority,
        severity=req.severity,
        lead_analyst_id=req.lead_analyst_id,
        affected_assets=req.affected_assets,
        affected_identities=req.affected_identities,
        mitre_attack_techniques=req.mitre_attack_techniques,
        sla_target_hours=req.sla_target_hours,
        risk_score=req.risk_score
    )
    return await SOCCaseManagementService.get_case_details(db, tenant_id, case.id)


@router.get("/cases/{id}", summary="Get SOC Case Details")
async def get_case_details(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full case details including timeline, tasks, comments, and audit history."""
    tenant_id = context.tenant_id or "default-tenant"
    details = await SOCCaseManagementService.get_case_details(db, tenant_id, id)
    if not details:
        raise SentinelAIException(status_code=404, detail="SOC Case not found.")
    return details


@router.put("/cases/{id}/status", summary="Update SOC Case Status")
async def update_case_status(
    id: str,
    req: UpdateCaseStatusRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Transitions case status across the 9 lifecycle states."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SOCCaseManagementService.update_case_status(
        db=db,
        tenant_id=tenant_id,
        case_id=id,
        new_status=req.status
    )


@router.post("/cases/{id}/comments", summary="Add Comment to Case")
async def add_case_comment(
    id: str,
    req: AddCommentRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Adds an analyst investigation note / comment to a case."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SOCCaseManagementService.add_case_comment(
        db=db,
        tenant_id=tenant_id,
        case_id=id,
        author=req.author,
        comment_text=req.comment_text,
        is_internal=req.is_internal
    )


@router.post("/cases/{id}/tasks", summary="Add Task to Case")
async def add_case_task(
    id: str,
    req: AddTaskRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Adds a containment or investigation subtask to a case."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SOCCaseManagementService.add_case_task(
        db=db,
        tenant_id=tenant_id,
        case_id=id,
        title=req.title,
        description=req.description,
        assigned_to=req.assigned_to
    )


# ==================== Forensic Evidence Endpoints ====================

@router.post("/cases/{id}/evidence", summary="Attach Forensic Evidence to Case")
async def attach_evidence_to_case(
    id: str,
    req: RegisterEvidenceRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Registers and cryptographically fingerprints forensic evidence item."""
    tenant_id = context.tenant_id or "default-tenant"
    item = await EvidenceCustodyService.register_evidence(
        db=db,
        tenant_id=tenant_id,
        title=req.title,
        description=req.description,
        evidence_type=req.evidence_type,
        raw_payload=req.raw_payload,
        source_system=req.source_system,
        collected_by=req.collected_by,
        case_id=id
    )
    return {
        "id": item.id,
        "case_id": item.case_id,
        "title": item.title,
        "evidence_type": item.evidence_type,
        "sha256_hash": item.sha256_hash,
        "integrity_verified": item.integrity_verified,
        "collected_at": item.collected_at.isoformat()
    }


@router.get("/cases/{id}/evidence", summary="List Case Forensic Evidence")
async def list_case_evidence(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists all forensic evidence items attached to a case."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EvidenceCustodyService.list_case_evidence(db, tenant_id, case_id=id)


@router.get("/evidence/{id}/verify", summary="Verify Forensic Evidence SHA-256 Integrity")
async def verify_evidence_integrity(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Recalculates SHA-256 hash against current stored payload to verify zero data tampering."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EvidenceCustodyService.verify_evidence_integrity(db, tenant_id, id)


@router.post("/evidence/{id}/transfer", summary="Record Forensic Custody Transfer")
async def transfer_evidence_custody(
    id: str,
    req: TransferCustodyRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Records an immutable chain of custody transfer event."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EvidenceCustodyService.transfer_custody(
        db=db,
        tenant_id=tenant_id,
        evidence_id=id,
        source_custodian=req.source_custodian,
        target_custodian=req.target_custodian,
        action=req.action,
        notes=req.notes
    )
