from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.threat_intelligence_platform_service import ThreatIntelligencePlatformService
from backend.app.models.threat_intel_platform import ThreatActor, ThreatCampaign, MalwareFamily, IndicatorSighting
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/threat-intelligence", tags=["Advanced Threat Intelligence Platform"])


class CreateActorRequest(BaseModel):
    name: str
    aliases: Optional[List[str]] = None
    actor_type: Optional[str] = "NATION_STATE"
    origin_country: Optional[str] = None
    motivation: Optional[str] = "ESPIONAGE"
    sophistication: Optional[str] = "HIGH"
    confidence_score: Optional[float] = 0.90
    ttp_list: Optional[List[str]] = None
    description: Optional[str] = None


class CreateCampaignRequest(BaseModel):
    name: str
    actor_id: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = "Data Exfiltration"
    malware_families: Optional[List[str]] = None
    targeted_sectors: Optional[List[str]] = None
    targeted_countries: Optional[List[str]] = None


class CorrelateIndicatorRequest(BaseModel):
    ioc_value: str


class RecordSightingRequest(BaseModel):
    indicator_id: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    sensor_id: Optional[str] = None


@router.get("/actors", summary="List Threat Actors")
async def list_threat_actors(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all profiled threat actors for the tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    stmt = select(ThreatActor).where(ThreatActor.tenant_id == tenant_id)
    actors = list((await db.execute(stmt)).scalars().all())
    return [
        {
            "id": a.id,
            "name": a.name,
            "aliases": a.aliases,
            "actor_type": a.actor_type,
            "origin_country": a.origin_country,
            "motivation": a.motivation,
            "sophistication": a.sophistication,
            "confidence_score": a.confidence_score,
            "ttp_list": a.ttp_list,
            "description": a.description
        }
        for a in actors
    ]


@router.post("/actors", summary="Create Threat Actor Profile")
async def create_threat_actor(
    payload: CreateActorRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new threat actor profile."""
    tenant_id = context.tenant_id or "default-tenant"
    actor = ThreatActor(
        tenant_id=tenant_id,
        name=payload.name,
        aliases=payload.aliases or [],
        actor_type=payload.actor_type or "NATION_STATE",
        origin_country=payload.origin_country,
        motivation=payload.motivation or "ESPIONAGE",
        sophistication=payload.sophistication or "HIGH",
        confidence_score=payload.confidence_score or 0.90,
        ttp_list=payload.ttp_list or [],
        description=payload.description
    )
    db.add(actor)
    await db.flush()
    return {"status": "CREATED", "actor_id": actor.id, "name": actor.name}


@router.get("/campaigns", summary="List Threat Campaigns")
async def list_threat_campaigns(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all active and historical attack campaigns."""
    tenant_id = context.tenant_id or "default-tenant"
    stmt = select(ThreatCampaign).where(ThreatCampaign.tenant_id == tenant_id)
    campaigns = list((await db.execute(stmt)).scalars().all())
    return [
        {
            "id": c.id,
            "name": c.name,
            "actor_id": c.actor_id,
            "description": c.description,
            "objective": c.objective,
            "malware_families": c.malware_families,
            "targeted_sectors": c.targeted_sectors,
            "confidence": c.confidence,
            "is_active": c.is_active
        }
        for c in campaigns
    ]


@router.post("/campaigns", summary="Create Threat Campaign")
async def create_threat_campaign(
    payload: CreateCampaignRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Registers a coordinated malicious campaign."""
    tenant_id = context.tenant_id or "default-tenant"
    campaign = ThreatCampaign(
        tenant_id=tenant_id,
        name=payload.name,
        actor_id=payload.actor_id,
        description=payload.description,
        objective=payload.objective or "Data Exfiltration",
        malware_families=payload.malware_families or [],
        targeted_sectors=payload.targeted_sectors or [],
        targeted_countries=payload.targeted_countries or [],
        confidence=0.88,
        is_active=True
    )
    db.add(campaign)
    await db.flush()
    return {"status": "CREATED", "campaign_id": campaign.id, "name": campaign.name}


@router.post("/correlate", summary="Correlate IOC with Telemetry & Alerts")
async def correlate_indicator(
    payload: CorrelateIndicatorRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Cross-correlates an indicator across all alerts, incidents, and sightings."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ThreatIntelligencePlatformService.correlate_indicator(
        db=db,
        tenant_id=tenant_id,
        ioc_value=payload.ioc_value
    )


@router.post("/sightings", summary="Record Customer Network Sighting")
async def record_sighting(
    payload: RecordSightingRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Records an empirical network sensor sighting for an indicator."""
    tenant_id = context.tenant_id or "default-tenant"
    sighting = await ThreatIntelligencePlatformService.record_sighting(
        db=db,
        tenant_id=tenant_id,
        indicator_id=payload.indicator_id,
        source_ip=payload.source_ip,
        destination_ip=payload.destination_ip,
        sensor_id=payload.sensor_id
    )
    return {"status": "RECORDED", "sighting_id": sighting.id, "sighted_at": sighting.sighted_at.isoformat()}


@router.post("/feeds/{id}/sync", summary="Synchronize Threat Intelligence Feed")
async def sync_threat_feed(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Triggers feed synchronization with SSRF protection and deduplication."""
    return await ThreatIntelligencePlatformService.sync_threat_feed(db, id)
