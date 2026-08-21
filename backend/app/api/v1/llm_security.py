"""
backend/app/api/v1/llm_security.py
==================================
Phase 30 AI/LLM Application Security, LLM-as-a-Target Defense & Shadow AI API Router.
Exposes:
- OWASP Top 10 for LLMs AI Posture Scorecard
- Real-Time Prompt Firewall & Guardrail Inspection Proxy
- LLM Threat Events & Prompt Injection Audit Ledger
- Shadow AI Discovery & Employee Endpoint Governance
- RAG & Vector Database Security Auditor
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.llm_guardrail_service import LLMGuardrailService
from backend.app.services.shadow_ai_service import ShadowAIService
from backend.app.services.rag_security_service import RAGSecurityService
from backend.app.services.ai_posture_service import AIPostureService

router = APIRouter(prefix="/llm-security", tags=["Phase 30 - AI/LLM Security & Shadow AI"])


# ==================== Request Payloads ====================

class InspectPromptRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text to inspect and sanitize")
    user_principal: str = Field(default="dev.analyst@aegivanta.io")
    source_ip: str = Field(default="10.0.8.44")


class BlockShadowAIRequest(BaseModel):
    block: bool = Field(default=True)


class ScanVectorDBRequest(BaseModel):
    db_type: str = Field(default="CHROMA_DB", example="CHROMA_DB")
    collection_name: str = Field(..., example="customer_rag_kb")
    total_embeddings: int = Field(default=10000, ge=1)


# ==================== Endpoints ====================

@router.get("/summary", summary="Get AI/LLM Security & OWASP Top 10 Scorecard")
async def get_ai_security_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates unified AI/LLM security posture score and key metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await AIPostureService.get_summary(db=db, tenant_id=tenant_id)


# Guardrail Proxy
@router.post("/guardrails/inspect", summary="Inspect Prompt Through Guardrail Firewall")
async def inspect_prompt(
    req: InspectPromptRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Inspects prompt inputs for injection attacks, PII, and system prompt leaks."""
    tenant_id = context.tenant_id or "default-tenant"
    return await LLMGuardrailService.inspect_prompt(
        db=db,
        tenant_id=tenant_id,
        prompt=req.prompt,
        user_principal=req.user_principal,
        source_ip=req.source_ip
    )


@router.get("/events", summary="List LLM Security Threat Events")
async def list_llm_events(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists audit events for prompt injections, jailbreaks, and PII extractions."""
    tenant_id = context.tenant_id or "default-tenant"
    return await LLMGuardrailService.list_events(db=db, tenant_id=tenant_id, limit=limit)


# Shadow AI Governance
@router.get("/shadow-ai", summary="List Discovered Shadow AI Tools")
async def list_shadow_ai_tools(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists consumer GenAI tools discovered on corporate network."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ShadowAIService.list_discovered_apps(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/shadow-ai/block/{record_id}", summary="Block/Unblock Shadow AI Application")
async def toggle_shadow_ai_block(
    record_id: str,
    req: BlockShadowAIRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Blocks or unblocks a Shadow AI application for corporate endpoints."""
    tenant_id = context.tenant_id or "default-tenant"
    res = await ShadowAIService.toggle_block_status(
        db=db,
        tenant_id=tenant_id,
        record_id=record_id,
        block=req.block
    )
    return res or {"error": "Record not found"}


# Vector DB Security
@router.get("/vectordb/audits", summary="List Vector DB Security Audits")
async def list_vectordb_audits(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists vector database security audit records."""
    tenant_id = context.tenant_id or "default-tenant"
    return await RAGSecurityService.list_audits(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/vectordb/scan", summary="Scan Vector DB Collection")
async def scan_vectordb_collection(
    req: ScanVectorDBRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Runs a live security audit on a target vector DB index."""
    tenant_id = context.tenant_id or "default-tenant"
    return await RAGSecurityService.scan_collection(
        db=db,
        tenant_id=tenant_id,
        db_type=req.db_type,
        collection_name=req.collection_name,
        total_embeddings=req.total_embeddings
    )
