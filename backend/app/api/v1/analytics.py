import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.incident import Incident
from backend.app.models.model_registry import ModelRegistry
from backend.app.schemas.analytics import AnalyticsSummary, AttackDistributionItem, ModelPerformanceItem
from backend.app.core.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Telemetry"])


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
