"""
backend/app/api/v1/analytics.py
===============================
Telemetry, Research Analytics, Behavioral Baselines & Anomaly Endpoints.
Preserves all Phase 1 analytics contracts and adds Phase 2 behavioral metrics.
"""

import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.model_registry import ModelRegistry
from backend.app.models.behavioral import BehavioralBaseline, AnomalyEvent
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.monitoring import MonitoringCheck
from backend.app.schemas.analytics import AnalyticsSummary, AttackDistributionItem, ModelPerformanceItem
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Telemetry"])


# =========================================================================
# PHASE 1 AUTHORITATIVE ANALYTICS CONTRACTS (FROZEN)
# =========================================================================

@router.get("/summary", response_model=AnalyticsSummary, summary="Get Dashboard Threat Analytics Summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Computes real-time threat summary metrics, attack distributions, and top malicious source IPs."""
    # Count total incidents
    total_query = select(func.count(Incident.id))
    total_res = await db.execute(total_query)
    total_packets = total_res.scalar() or 0

    # Count threats
    threats_query = select(func.count(Incident.id)).where(Incident.is_malicious == True)
    threats_res = await db.execute(threats_query)
    total_threats = threats_res.scalar() or 0

    # Count criticals
    critical_query = select(func.count(Incident.id)).where(Incident.severity == "Critical")
    critical_res = await db.execute(critical_query)
    critical_count = critical_res.scalar() or 0

    # Network status determination
    if critical_count > 5 or total_threats > 20:
        network_status = "CRITICAL"
    elif total_threats > 0:
        network_status = "WARNING"
    else:
        network_status = "SECURE"

    # Attack Type distribution
    dist_query = (
        select(Incident.attack_type, func.count(Incident.id).label("cnt"))
        .group_by(Incident.attack_type)
        .order_by(desc("cnt"))
    )
    dist_res = await db.execute(dist_query)
    dist_rows = dist_res.all()

    attack_distribution: List[AttackDistributionItem] = []
    for attack_type, count in dist_rows:
        pct = round((count / total_packets * 100.0), 2) if total_packets > 0 else 0.0
        attack_distribution.append(AttackDistributionItem(
            attack_type=attack_type,
            count=count,
            percentage=pct
        ))

    # Top Source IPs
    ip_query = (
        select(Incident.source_ip, func.count(Incident.id).label("cnt"))
        .where(Incident.is_malicious == True)
        .group_by(Incident.source_ip)
        .order_by(desc("cnt"))
        .limit(5)
    )
    ip_res = await db.execute(ip_query)
    top_ips = [{"ip": row[0], "count": row[1]} for row in ip_res.all()]

    # Model Performance List
    models_query = select(ModelRegistry).order_by(ModelRegistry.f1_score.desc())
    models_res = await db.execute(models_query)
    models_list = models_res.scalars().all()

    model_performance: List[ModelPerformanceItem] = [
        ModelPerformanceItem(
            model_name=m.model_name,
            model_type=m.model_type,
            accuracy=m.accuracy,
            f1_score=m.f1_score,
            precision_score=m.precision_score,
            recall_score=m.recall_score,
            roc_auc=m.roc_auc,
            is_active=m.is_active
        )
        for m in models_list
    ]

    # Recent Incidents
    rec_query = select(Incident).order_by(Incident.timestamp.desc()).limit(10)
    rec_res = await db.execute(rec_query)
    recent = [
        {
            "id": inc.id,
            "source_ip": inc.source_ip,
            "destination_ip": inc.destination_ip,
            "attack_type": inc.attack_type,
            "confidence_score": inc.confidence_score,
            "is_malicious": inc.is_malicious,
            "severity": inc.severity,
            "timestamp": inc.timestamp.isoformat()
        }
        for inc in rec_res.scalars().all()
    ]

    active_model = next((m for m in models_list if m.is_active), None)
    active_model_name = active_model.model_name if active_model else "Unavailable"

    return AnalyticsSummary(
        network_status=network_status,
        total_packets_inspected=total_packets,
        total_threats_detected=total_threats,
        critical_incidents_count=critical_count,
        prediction_accuracy=active_model.accuracy if active_model else 0.0,
        active_model=active_model_name,
        attack_distribution=attack_distribution,
        model_performance=model_performance,
        top_source_ips=top_ips,
        recent_incidents=recent
    )


@router.get("/roc", summary="Get Model ROC Curves data")
async def get_roc_curves(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serves dynamic active model ROC curve and versioned historical research benchmarks."""
    historical_file = Path("research/reference/historical_benchmarks.json")
    historical_baselines = []
    if historical_file.exists():
        try:
            with open(historical_file, "r", encoding="utf-8") as f:
                ref_data = json.load(f)
                historical_baselines = ref_data.get("baselines", [])
        except Exception:
            pass

    roc_json_path = Path("ml/artifacts/roc_curves.json")
    if roc_json_path.exists():
        try:
            with open(roc_json_path, "r", encoding="utf-8") as f:
                curves_data = json.load(f)
            curves_data["historical_baselines"] = historical_baselines
            return curves_data
        except Exception:
            pass

    return {
        "status": "unavailable",
        "active_model": None,
        "historical_baselines": historical_baselines
    }


# =========================================================================
# PHASE 2 ADDITIVE BEHAVIORAL & ADVANCED SOC ANALYTICS
# =========================================================================

@router.get("/anomalies", summary="List Behavioral Anomaly Events")
async def list_anomalies(
    asset_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves detected behavioral anomaly events with explainable reasoning."""
    query = select(AnomalyEvent)
    if asset_id:
        query = query.where(AnomalyEvent.asset_id == asset_id)
    if severity:
        query = query.where(AnomalyEvent.severity == severity.upper())
    query = query.order_by(AnomalyEvent.timestamp.desc()).limit(limit)

    res = await db.execute(query)
    anomalies = res.scalars().all()
    return [
        {
            "id": a.id,
            "asset_id": a.asset_id,
            "metric_name": a.metric_name,
            "observed_value": a.observed_value,
            "baseline_mean": a.baseline_mean,
            "baseline_std": a.baseline_std,
            "z_score": a.z_score,
            "anomaly_score": a.anomaly_score,
            "severity": a.severity,
            "explanation": a.explanation,
            "status": a.status,
            "timestamp": a.timestamp.isoformat() if a.timestamp else None
        }
        for a in anomalies
    ]


@router.get("/baselines/{asset_id}", summary="Get Asset Statistical Baselines")
async def get_asset_baselines(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves rolling behavioral baselines for a specific protected asset."""
    query = select(BehavioralBaseline).where(BehavioralBaseline.asset_id == asset_id)
    res = await db.execute(query)
    baselines = res.scalars().all()
    return [
        {
            "metric_name": b.metric_name,
            "baseline_mean": b.baseline_mean,
            "baseline_std": b.baseline_std,
            "min_val": b.min_val,
            "max_val": b.max_val,
            "sample_count": b.sample_count,
            "updated_at": b.updated_at.isoformat() if b.updated_at else None
        }
        for b in baselines
    ]


@router.get("/metrics", summary="Get Advanced SOC Analytics Summary")
async def get_advanced_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aggregates high-level SOC metrics across alerts, IOCs, anomalies, and monitors."""
    # 1. Total Counts
    res_alerts = await db.execute(select(func.count(Alert.id)))
    total_alerts = res_alerts.scalar() or 0

    res_inc = await db.execute(select(func.count(Incident.id)))
    total_incidents = res_inc.scalar() or 0

    res_iocs = await db.execute(select(func.count(ThreatIndicator.id)).where(ThreatIndicator.is_active == True))
    active_iocs = res_iocs.scalar() or 0

    res_anom = await db.execute(select(func.count(AnomalyEvent.id)))
    total_anomalies = res_anom.scalar() or 0

    res_mon = await db.execute(select(func.count(MonitoringCheck.id)))
    monitored_targets = res_mon.scalar() or 0

    # 2. Attack Category Breakdown
    res_cat = await db.execute(
        select(Alert.attack_type, func.count(Alert.id))
        .group_by(Alert.attack_type)
        .order_by(func.count(Alert.id).desc())
        .limit(10)
    )
    attack_breakdown = [{"attack_type": row[0], "count": row[1]} for row in res_cat.all()]

    return {
        "total_alerts": total_alerts,
        "total_incidents": total_incidents,
        "active_threat_indicators": active_iocs,
        "total_anomalies_detected": total_anomalies,
        "monitored_endpoints": monitored_targets,
        "attack_distribution": attack_breakdown,
        "telemetry_status": "ONLINE"
    }
