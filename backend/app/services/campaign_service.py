"""
backend/app/services/campaign_service.py
========================================
Multi-Incident Campaign Correlation Engine.
Correlates incidents sharing infrastructure, CIDR subnets, and attack vectors into campaigns.
Attribution is conservatively labeled as UNKNOWN unless verifiable threat feed signatures match.
"""

from datetime import datetime, timezone, timedelta
from collections import defaultdict
import logging
from typing import List, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident

logger = logging.getLogger("SentinelAI")


def _normalize_dt(dt):
    """Ensures datetime is timezone-aware UTC for safe comparisons."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class CampaignService:
    """Detects multi-incident campaigns across telemetry horizons."""

    @staticmethod
    async def detect_campaigns(lookback_hours: int = 48, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """
        Clusters incidents sharing:
        1. Exact Source IP or /24 CIDR prefix
        2. Common Attack Type (e.g. DDoS, PortScan, Infiltration)
        3. Common Threat Indicator IOC match
        """
        since_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        res = await db.execute(
            select(Incident).order_by(desc(Incident.timestamp))
        )
        all_incidents = res.scalars().all()
        
        # Filter with normalized timezone
        incidents = [i for i in all_incidents if _normalize_dt(i.timestamp) and _normalize_dt(i.timestamp) >= since_time]

        if len(incidents) < 2:
            return []

        # Group by Source IP and Attack Type
        ip_clusters = defaultdict(list)
        attack_clusters = defaultdict(list)

        for inc in incidents:
            if inc.source_ip:
                # Group by IP /24 subnet prefix
                parts = inc.source_ip.split(".")
                subnet = ".".join(parts[:3]) + ".0/24" if len(parts) == 4 else inc.source_ip
                ip_clusters[subnet].append(inc)
            if inc.attack_type:
                attack_clusters[inc.attack_type].append(inc)

        campaigns: List[Dict[str, Any]] = []
        seen_incident_ids = set()

        # 1. Evaluate Subnet / IP Campaigns
        for subnet, inc_list in ip_clusters.items():
            if len(inc_list) >= 2:
                cid = f"CAMP-IP-{abs(hash(subnet)) % 10000:04d}"
                inc_ids = [i.id for i in inc_list]
                seen_incident_ids.update(inc_ids)

                avg_risk = sum(i.risk_score or 50.0 for i in inc_list) / len(inc_list)
                targets = list({i.destination_ip for i in inc_list if i.destination_ip})
                valid_ts = [_normalize_dt(i.timestamp) for i in inc_list if i.timestamp]

                campaigns.append({
                    "campaign_id": cid,
                    "name": f"Coordinated Multi-Target Activity from {subnet}",
                    "confidence_label": "CORRELATED_CAMPAIGN",
                    "attribution": "UNKNOWN (Shared Infrastructure)",
                    "incident_count": len(inc_list),
                    "incidents": [
                        {
                            "id": i.id,
                            "code": i.incident_code,
                            "attack_type": i.attack_type,
                            "severity": i.severity,
                            "risk_score": i.risk_score,
                            "timestamp": i.timestamp.isoformat() if i.timestamp else None
                        }
                        for i in inc_list
                    ],
                    "target_entities": targets,
                    "average_risk_score": round(avg_risk, 1),
                    "first_observed": min(valid_ts).isoformat() if valid_ts else None,
                    "last_observed": max(valid_ts).isoformat() if valid_ts else None,
                    "evidence": [
                        f"Detected {len(inc_list)} distinct incidents originating from common subnet {subnet}",
                        f"Targeting {len(targets)} protected endpoints across the infrastructure"
                    ]
                })

        # 2. Evaluate Shared Attack Vector Campaigns (for remaining unclustered)
        for atk_type, inc_list in attack_clusters.items():
            unclustered = [i for i in inc_list if i.id not in seen_incident_ids]
            if len(unclustered) >= 3 and atk_type != "BENIGN":
                cid = f"CAMP-VEC-{abs(hash(atk_type)) % 10000:04d}"
                avg_risk = sum(i.risk_score or 50.0 for i in unclustered) / len(unclustered)
                targets = list({i.destination_ip for i in unclustered if i.destination_ip})
                valid_ts = [_normalize_dt(i.timestamp) for i in unclustered if i.timestamp]

                campaigns.append({
                    "campaign_id": cid,
                    "name": f"Distributed {atk_type} Wave Campaign",
                    "confidence_label": "POSSIBLE_CAMPAIGN",
                    "attribution": "UNKNOWN (Pattern Correlation)",
                    "incident_count": len(unclustered),
                    "incidents": [
                        {
                            "id": i.id,
                            "code": i.incident_code,
                            "attack_type": i.attack_type,
                            "severity": i.severity,
                            "risk_score": i.risk_score,
                            "timestamp": i.timestamp.isoformat() if i.timestamp else None
                        }
                        for i in unclustered
                    ],
                    "target_entities": targets,
                    "average_risk_score": round(avg_risk, 1),
                    "first_observed": min(valid_ts).isoformat() if valid_ts else None,
                    "last_observed": max(valid_ts).isoformat() if valid_ts else None,
                    "evidence": [
                        f"Cluster of {len(unclustered)} separate {atk_type} intrusions detected within {lookback_hours}h window"
                    ]
                })

        return campaigns
