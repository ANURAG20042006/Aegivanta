"""
backend/app/services/soc_metrics_service.py
===========================================
SOC Effectiveness & Operational Analytics Service.
Computes MTTD, MTTR, Alert-to-Incident ratios, False Positive metrics, and Analyst Workload distributions.
"""

from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any, List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.playbook import PlaybookExecution

logger = logging.getLogger("SentinelAI")


def _normalize_dt(dt):
    """Ensures datetime is timezone-aware UTC for safe comparisons."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class SOCMetricsService:
    """Computes empirical SOC performance and operational effectiveness metrics."""

    @staticmethod
    async def get_soc_overview(lookback_days: int = 30, db: AsyncSession = None) -> Dict[str, Any]:
        """
        Calculates high-level SOC effectiveness metrics over a specified lookback window.
        """
        since_time = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        # 1. Total Incidents & Alerts
        inc_res = await db.execute(select(Incident).order_by(desc(Incident.timestamp)))
        all_incidents = inc_res.scalars().all()
        incidents = [i for i in all_incidents if _normalize_dt(i.timestamp) and _normalize_dt(i.timestamp) >= since_time]
        
        alt_res = await db.execute(select(func.count(Alert.id)).where(Alert.timestamp >= since_time))
        total_alerts = alt_res.scalar() or 0

        # 2. MTTD & MTTR Calculations
        # MTTD: Average difference between first_seen and timestamp on correlated incidents
        mttd_seconds_list = []
        mttr_seconds_list = []

        for inc in incidents:
            ts = _normalize_dt(inc.timestamp)
            fs = _normalize_dt(inc.first_seen)
            ca = _normalize_dt(inc.closed_at)

            if fs and ts:
                delta = abs((ts - fs).total_seconds())
                mttd_seconds_list.append(delta)
            if inc.status in ["closed", "resolved", "CONTAINED", "RESOLVED"] and ts and ca:
                delta = abs((ca - ts).total_seconds())
                mttr_seconds_list.append(delta)

        avg_mttd_min = round((sum(mttd_seconds_list) / len(mttd_seconds_list)) / 60.0, 1) if mttd_seconds_list else None
        avg_mttr_min = round((sum(mttr_seconds_list) / len(mttr_seconds_list)) / 60.0, 1) if mttr_seconds_list else None

        # 3. Alert to Incident Compression Ratio
        total_incs = len(incidents)
        compression_ratio = round((total_alerts / total_incs), 1) if total_incs > 0 else 1.0

        # 4. Status Counts
        open_incs = sum(1 for i in incidents if i.status in ["open", "investigating", "DETECTED", "TRIAGED", "INVESTIGATING"])
        resolved_incs = sum(1 for i in incidents if i.status in ["closed", "resolved", "CONTAINED", "RESOLVED", "CLOSED"])

        # 5. False Positive Estimation (based on closed incidents with 'benign' resolution)
        fp_count = sum(1 for i in incidents if "benign" in str(i.resolution or "").lower() or i.attack_type == "BENIGN")
        fp_rate = round((fp_count / total_incs) * 100.0, 2) if total_incs > 0 else None

        return {
            "time_window_days": lookback_days,
            "sample_incidents_count": total_incs,
            "sample_alerts_count": total_alerts,
            "mttd_minutes": avg_mttd_min,
            "mttd_status": "calculated" if avg_mttd_min is not None else "insufficient_data",
            "mttr_minutes": avg_mttr_min,
            "mttr_status": "calculated" if avg_mttr_min is not None else "insufficient_data",
            "open_incidents": open_incs,
            "resolved_incidents": resolved_incs,
            "alert_to_incident_ratio": compression_ratio,
            "estimated_false_positive_rate_pct": fp_rate,
            "false_positive_status": "calculated" if fp_rate is not None else "insufficient_data",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    async def get_analyst_workload(db: AsyncSession) -> Dict[str, Any]:
        """Calculates analyst playbook and containment execution workload distribution."""
        res_pb = await db.execute(select(PlaybookExecution).limit(100))
        executions = res_pb.scalars().all()

        actor_counts = {}
        for ex in executions:
            actor = ex.executed_by or "system"
            actor_counts[actor] = actor_counts.get(actor, 0) + 1

        return {
            "total_executions": len(executions),
            "distribution_by_analyst": actor_counts
        }
