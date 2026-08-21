"""
backend/app/api/v1/threat_intel_v2.py
=====================================
Phase 32 Cyber Threat Intelligence (CTI) 2.0 & STIX/TAXII 2.1 API Router.
Exposes:
- CTI 2.0 & Threat Landscape Summary Scorecard
- Threat Actor Intelligence Profiles & Diamond Model Attribution
- STIX 2.1 / TAXII 2.1 Feed Management & On-Demand Polling
- Dynamic IOC Ledger with Exponential Sighting Decay
- MITRE ATT&CK Campaign Technique Heatmap Navigator
- Automated Threat Hunting Query Generator
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.stix_taxii_engine_service import STIXTAXIIEngineService
from backend.app.services.threat_actor_profiling_service import ThreatActorProfilingService
from backend.app.services.ioc_decay_service import IOCDecayService
from backend.app.services.cti_posture_service import CTIPostureService

router = APIRouter(prefix="/threat-intel-v2", tags=["Phase 32 - Cyber Threat Intelligence 2.0"])


# ==================== Request Payloads ====================

class GenerateHuntingQueriesRequest(BaseModel):
    actor_name: str = Field(default="Volt Typhoon", example="Volt Typhoon")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get CTI 2.0 Posture & Threat Landscape Summary")
async def get_cti_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated CTI posture score and global threat metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CTIPostureService.get_summary(db=db, tenant_id=tenant_id)


# Threat Actors
@router.get("/actors", summary="List Threat Actor Profiles & Diamond Model Data")
async def list_threat_actors(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists nation-state and eCrime threat actor profiles."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ThreatActorProfilingService.list_actors(db=db, tenant_id=tenant_id, limit=limit)


# STIX / TAXII Feeds
@router.get("/feeds", summary="List STIX 2.1 / TAXII 2.1 Feed Sources")
async def list_stix_feeds(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists automated STIX/TAXII threat feed subscriptions."""
    tenant_id = context.tenant_id or "default-tenant"
    return await STIXTAXIIEngineService.list_feed_sources(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/feeds/poll/{feed_id}", summary="Poll STIX/TAXII Feed Immediately")
async def poll_stix_feed(
    feed_id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Triggers an on-demand poll and ingestion from the TAXII server."""
    tenant_id = context.tenant_id or "default-tenant"
    res = await STIXTAXIIEngineService.poll_feed_now(db=db, tenant_id=tenant_id, feed_id=feed_id)
    return res or {"error": "Feed not found"}


# IOC Ledger with Decay
@router.get("/indicators", summary="List Indicators with Dynamic Sighting Decay")
async def list_indicators(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists CTI indicators with real-time decayed confidence scores."""
    tenant_id = context.tenant_id or "default-tenant"
    return await IOCDecayService.list_indicators(db=db, tenant_id=tenant_id, limit=limit)


# Campaign Heatmaps
@router.get("/campaigns/heatmap", summary="List MITRE ATT&CK Campaign Technique Heatmaps")
async def list_campaign_heatmaps(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists MITRE ATT&CK techniques with threat heat levels."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ThreatActorProfilingService.list_campaign_heatmaps(db=db, tenant_id=tenant_id)


# Automated Threat Hunting Queries
@router.post("/hunting/generate-queries", summary="Auto-Generate Threat Hunting Queries")
async def generate_threat_hunting_queries(
    req: GenerateHuntingQueriesRequest,
    context: TenantContext = Depends(resolve_tenant_context)
):
    """Generates KQL and SPL threat hunting queries mapped to threat actor TTPs."""
    return CTIPostureService.generate_hunting_queries(actor_name=req.actor_name)
