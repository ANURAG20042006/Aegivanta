from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.services.detection_content_service import DetectionContentService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/detection-rules", tags=["Detection Content & Rules"])


class CreateRuleRequest(BaseModel):
    rule_code: str
    name: str
    rule_dsl: Dict[str, Any]
    severity: Optional[str] = "HIGH"
    confidence: Optional[float] = 0.85
    mitre_attack_mappings: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    version: Optional[str] = "1.0.0"


class TestRuleRequest(BaseModel):
    rule_dsl: Dict[str, Any]
    sample_events: List[Dict[str, Any]]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create or Update Detection Rule")
async def create_detection_rule(
    payload: CreateRuleRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.SECURITY_ANALYST)),
    db: AsyncSession = Depends(get_db)
):

    """Creates or updates a versioned Detection-as-Code rule."""
    is_valid, error = DetectionContentService.validate_rule(payload.model_dump())
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    rule = await DetectionContentService.create_or_update_rule(
        db=db,
        rule_code=payload.rule_code,
        name=payload.name,
        rule_dsl=payload.rule_dsl,
        severity=payload.severity or "HIGH",
        confidence=payload.confidence or 0.85,
        mitre_attack_mappings=payload.mitre_attack_mappings,
        description=payload.description,
        version=payload.version or "1.0.0",
        organization_id=context.organization_id
    )
    await db.commit()
    return {
        "id": rule.id,
        "rule_code": rule.rule_code,
        "name": rule.name,
        "version": rule.version,
        "severity": rule.severity,
        "status": rule.status
    }


@router.post("/test", summary="Test Rule Against Telemetry Sandbox")
async def test_detection_rule(
    payload: TestRuleRequest,
    context: TenantContext = Depends(resolve_tenant_context)
):
    """Tests rule DSL conditions against sample event vectors in an isolated sandbox."""
    return await DetectionContentService.test_rule(payload.rule_dsl, payload.sample_events)


@router.get("", summary="List Detection Rules")
async def list_detection_rules(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists all detection rules active for the tenant and global Aegivanta marketplace."""
    rules = await DetectionContentService.list_rules(db, organization_id=context.organization_id)
    return [
        {
            "id": r.id,
            "rule_code": r.rule_code,
            "name": r.name,
            "version": r.version,
            "author": r.author,
            "severity": r.severity,
            "confidence": r.confidence,
            "status": r.status,
            "mitre_attack_mappings": r.mitre_attack_mappings
        }
        for r in rules
    ]
