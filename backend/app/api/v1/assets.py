"""
backend/app/api/v1/assets.py
============================
Protected Assets Management API Endpoints.
Full CRUD, Health & Operational Risk Profiling with strict RBAC enforcement.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.core.auth import get_current_user, require_role
from backend.app.core.logging import logger
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetResponse, AssetListResponse, AssetHealthSummary
)
from backend.app.services.risk_engine import RiskScoringEngine


router = APIRouter(prefix="/assets", tags=["Protected Assets"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED, summary="Register New Protected Asset")
async def create_asset(
    payload: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Registers a new monitored asset (Website, API, Server, Database, Endpoint, Network).
    Restricted to Admin and Security Analyst roles.
    """
    # Check for active duplicate hostname or name
    stmt = select(ProtectedAsset).where(
        and_(
            ProtectedAsset.status != "inactive",
            or_(
                ProtectedAsset.hostname == payload.hostname,
                ProtectedAsset.name == payload.name
            )
        )
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An asset with name '{payload.name}' or hostname '{payload.hostname}' already exists."
        )

    asset = ProtectedAsset(
        name=payload.name,
        hostname=payload.hostname,
        url=payload.url,
        ip_address=payload.ip_address,
        asset_type=payload.asset_type,
        environment=payload.environment,
        criticality=payload.criticality,
        status=payload.status,
        description=payload.description,
        tags=payload.tags or {},
        risk_score=0.0
    )
    db.add(asset)
    await db.flush()

    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_PROTECTED_ASSET",
        resource="PROTECTED_ASSETS",
        details={"message": f"Created asset '{asset.name}' ({asset.asset_type}) with criticality '{asset.criticality}'."}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(asset)

    logger.info("Asset created: %s (%s) by %s", asset.name, asset.id, current_user.username)
    return asset


@router.get("", response_model=AssetListResponse, summary="List and Filter Protected Assets")
async def list_assets(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    criticality: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Paginated retrieval of protected assets with server-side filters.
    Accessible to all authenticated roles (Admin, Analyst, Viewer).
    """
    filters = []
    if asset_type:
        filters.append(ProtectedAsset.asset_type == asset_type.lower())
    if environment:
        filters.append(ProtectedAsset.environment == environment.lower())
    if criticality:
        filters.append(ProtectedAsset.criticality == criticality.lower())
    if status_filter:
        filters.append(ProtectedAsset.status == status_filter.lower())
    if search:
        search_fmt = f"%{search}%"
        filters.append(
            or_(
                ProtectedAsset.name.ilike(search_fmt),
                ProtectedAsset.hostname.ilike(search_fmt),
                ProtectedAsset.ip_address.ilike(search_fmt)
            )
        )

    total_stmt = select(func.count(ProtectedAsset.id)).where(*filters)
    total = (await db.execute(total_stmt)).scalar_one()

    offset = (page - 1) * size
    query = select(ProtectedAsset).where(*filters).order_by(ProtectedAsset.risk_score.desc(), ProtectedAsset.updated_at.desc()).offset(offset).limit(size)
    result = (await db.execute(query)).scalars().all()

    return AssetListResponse(
        total=total,
        page=page,
        size=size,
        items=result
    )


@router.get("/summary/stats", summary="Get Protected Assets Aggregate Summary")
async def get_assets_summary_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns high-level aggregate counts of protected assets by status and criticality."""
    total = (await db.execute(select(func.count(ProtectedAsset.id)))).scalar_one()
    active = (await db.execute(select(func.count(ProtectedAsset.id)).where(ProtectedAsset.status == "active"))).scalar_one()
    compromised = (await db.execute(select(func.count(ProtectedAsset.id)).where(ProtectedAsset.status == "compromised"))).scalar_one()
    degraded = (await db.execute(select(func.count(ProtectedAsset.id)).where(ProtectedAsset.status == "degraded"))).scalar_one()
    high_risk = (await db.execute(select(func.count(ProtectedAsset.id)).where(ProtectedAsset.risk_score >= 50.0))).scalar_one()

    return {
        "total_assets": total,
        "active_healthy": active,
        "degraded": degraded,
        "compromised": compromised,
        "high_or_critical_risk_assets": high_risk
    }


@router.get("/{asset_id}", response_model=AssetResponse, summary="Get Single Asset Details")
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves full metadata for a single protected asset."""
    asset = (await db.execute(select(ProtectedAsset).where(ProtectedAsset.id == asset_id))).scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protected Asset not found.")
    return asset


@router.get("/{asset_id}/health", response_model=AssetHealthSummary, summary="Get Asset Health & Risk Profile")
async def get_asset_health(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Computes comprehensive health, active incidents count, and risk breakdown for an asset."""
    asset = (await db.execute(select(ProtectedAsset).where(ProtectedAsset.id == asset_id))).scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protected Asset not found.")

    active_incidents = (await db.execute(
        select(func.count(Incident.id)).where(
            and_(
                Incident.asset_id == asset.id,
                Incident.status.in_(["DETECTED", "TRIAGED", "INVESTIGATING"])
            )
        )
    )).scalar_one()

    total_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.asset_id == asset.id)
    )).scalar_one()

    return AssetHealthSummary(
        asset_id=asset.id,
        name=asset.name,
        status=asset.status,
        criticality=asset.criticality,
        risk_score=asset.risk_score,
        risk_tier=RiskScoringEngine.get_risk_tier(asset.risk_score),
        active_incidents_count=active_incidents,
        total_alerts_count=total_alerts,
        last_seen=asset.last_seen
    )


@router.put("/{asset_id}", response_model=AssetResponse, summary="Update Protected Asset")
async def update_asset(
    asset_id: str,
    payload: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Updates protected asset properties. Restricted to Admin and Analyst."""
    asset = (await db.execute(select(ProtectedAsset).where(ProtectedAsset.id == asset_id))).scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protected Asset not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(asset, k, v)

    audit = AuditLog(
        user_id=current_user.id,
        action="UPDATE_PROTECTED_ASSET",
        resource="PROTECTED_ASSETS",
        details={"message": f"Updated asset '{asset.name}' fields: {list(update_data.keys())}."}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(asset)

    logger.info("Asset updated: %s by %s", asset.id, current_user.username)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deactivate / Soft-Delete Protected Asset")
async def delete_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Deactivates (soft-deletes) a protected asset, preserving historical alerts,
    correlations, and foreign key integrity. Restricted to Admin.
    """
    asset = (await db.execute(select(ProtectedAsset).where(ProtectedAsset.id == asset_id))).scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protected Asset not found.")

    asset.status = "inactive"
    asset.updated_at = datetime.now(timezone.utc)

    audit = AuditLog(
        user_id=current_user.id,
        action="DEACTIVATE_PROTECTED_ASSET",
        resource="PROTECTED_ASSETS",
        details={"message": f"Deactivated/Soft-deleted protected asset '{asset.name}' (Hostname: {asset.hostname})."}
    )
    db.add(audit)
    await db.commit()

    logger.info("Asset deactivated (soft-deleted): %s by %s", asset_id, current_user.username)
    return None
