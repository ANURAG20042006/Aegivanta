"""
backend/app/api/v1/threat_intel.py
==================================
Threat Intelligence & IOC Management API Endpoints.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.threat_intel import ThreatIndicator, ThreatFeed
from backend.app.services.threat_intel_service import ThreatIntelService, normalize_ioc

router = APIRouter(prefix="/threat-intel", tags=["Threat Intelligence & IOCs"])


class ThreatIndicatorCreate(BaseModel):
    raw_value: str = Field(..., description="IP, Domain, URL, or File Hash")
    ioc_type: str = Field("ipv4", description="Indicator type: ipv4, ipv6, domain, url, sha256, md5")
    threat_type: str = Field("malicious_host", description="Threat classification (c2, botnet, scanner, bruteforce)")
    severity: str = Field("HIGH", description="Severity level: CRITICAL, HIGH, MEDIUM, LOW, INFO")
    confidence: float = Field(0.85, ge=0.0, le=1.0)
    source: str = Field("Local_SOC", description="Attribution feed source")
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class IOCLookupRequest(BaseModel):
    value: str = Field(..., description="IP or domain to check against threat intelligence")


@router.get("/indicators", summary="List Threat Intelligence Indicators")
async def list_indicators(
    ioc_type: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves paginated threat indicators with optional type/severity filters."""
    query = select(ThreatIndicator).where(ThreatIndicator.is_active == True)
    if ioc_type:
        query = query.where(ThreatIndicator.ioc_type == ioc_type.lower())
    if severity:
        query = query.where(ThreatIndicator.severity == severity.upper())
    if search:
        query = query.where(ThreatIndicator.normalized_value.contains(search.lower().strip()))
    query = query.order_by(ThreatIndicator.last_seen.desc()).limit(limit)

    res = await db.execute(query)
    indicators = res.scalars().all()
    return [
        {
            "id": ind.id,
            "ioc_type": ind.ioc_type,
            "raw_value": ind.raw_value,
            "normalized_value": ind.normalized_value,
            "threat_type": ind.threat_type,
            "severity": ind.severity,
            "confidence": ind.confidence,
            "source": ind.source,
            "description": ind.description,
            "tags": ind.tags or [],
            "hit_count": ind.hit_count,
            "last_seen": ind.last_seen.isoformat() if ind.last_seen else None
        }
        for ind in indicators
    ]


@router.post("/indicators", status_code=status.HTTP_201_CREATED, summary="Add Threat Indicator")
async def create_indicator(
    payload: ThreatIndicatorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Adds a new normalized threat intelligence indicator."""
    is_valid, norm_val, det_type = normalize_ioc(payload.raw_value, payload.ioc_type)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid indicator format for type '{payload.ioc_type}'."
        )

    # Check for existing indicator
    q = select(ThreatIndicator).where(ThreatIndicator.normalized_value == norm_val)
    existing_res = await db.execute(q)
    existing = existing_res.scalar_one_or_none()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if existing:
        existing.last_seen = now
        existing.is_active = True
        existing.severity = payload.severity.upper()
        existing.confidence = payload.confidence
        existing.tags = payload.tags
        await db.commit()
        await db.refresh(existing)
        return {"status": "updated", "id": existing.id, "normalized_value": norm_val}

    indicator = ThreatIndicator(
        ioc_type=det_type,
        raw_value=payload.raw_value.strip(),
        normalized_value=norm_val,
        threat_type=payload.threat_type,
        severity=payload.severity.upper(),
        confidence=payload.confidence,
        source=payload.source,
        description=payload.description,
        tags=payload.tags,
        first_seen=now,
        last_seen=now,
        is_active=True
    )
    db.add(indicator)
    await db.commit()
    await db.refresh(indicator)

    return {
        "status": "created",
        "id": indicator.id,
        "normalized_value": norm_val,
        "ioc_type": det_type,
        "severity": indicator.severity
    }


@router.post("/lookup", summary="Lookup Indicator in Threat Intelligence")
async def lookup_indicator(
    payload: IOCLookupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queries whether an IP or domain matches known threat intelligence indicators."""
    val = payload.value.strip()
    result = await ThreatIntelService.enrich_telemetry(val, val, val, db)
    await db.commit()
    return result


@router.get("/feeds", summary="List Configured Threat Intelligence Feeds")
async def list_feeds(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves configured threat intelligence feed sources and sync status."""
    res = await db.execute(select(ThreatFeed).order_by(ThreatFeed.created_at.desc()))
    feeds = res.scalars().all()
    return [
        {
            "id": f.id,
            "feed_name": f.feed_name,
            "provider_type": f.provider_type,
            "feed_url": f.feed_url,
            "last_synced_at": f.last_synced_at.isoformat() if f.last_synced_at else None,
            "last_sync_status": f.last_sync_status,
            "indicators_imported": f.indicators_imported,
            "is_active": f.is_active
        }
        for f in feeds
    ]


@router.post("/feeds/{feed_id}/sync", summary="Trigger Threat Feed Synchronization")
async def sync_feed_now(
    feed_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Triggers an on-demand feed synchronization."""
    query = select(ThreatFeed).where(ThreatFeed.id == feed_id)
    res = await db.execute(query)
    feed = res.scalar_one_or_none()
    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat feed not found.")

    imported = await ThreatIntelService.ingest_feed(feed, db)
    await db.commit()
    return {
        "feed_id": feed.id,
        "feed_name": feed.feed_name,
        "status": feed.last_sync_status,
        "indicators_imported": imported
    }
