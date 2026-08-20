"""
backend/app/services/advanced_hunting_service.py
================================================
Phase 18 Threat Hunting Workbench Service.
Supports multi-target hunting across IP, Domain, URL, Hash, User, Process,
Authentication, DNS, Flow, Lateral Movement, and MITRE ATT&CK Techniques.
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.hunting import HuntingQuery, HuntingExecution
from backend.app.models.alert import Alert
from backend.app.models.security_event import SecurityEvent
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.incident import Incident
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("Aegivanta.AdvancedHunting")

HUNT_TEMPLATES = [
    {
        "id": "TPL-01",
        "name": "High-Frequency Authentication Failures (Brute Force)",
        "entity_type": "AUTH",
        "technique": "T1110",
        "description": "Searches for anomalous login attempts exceeding 5 failures in 10 minutes.",
        "filters": [{"field": "attack_type", "operator": "equals", "value": "Brute Force"}]
    },
    {
        "id": "TPL-02",
        "name": "SMB / RPC Lateral Movement Probing",
        "entity_type": "LATERAL_MOVEMENT",
        "technique": "T1021",
        "description": "Identifies internal network hops across port 445 / 135.",
        "filters": [{"field": "attack_type", "operator": "equals", "value": "PortScan"}]
    },
    {
        "id": "TPL-03",
        "name": "Known Malicious C2 IP Indicators",
        "entity_type": "IP",
        "technique": "T1071",
        "description": "Hunts for outbound traffic matching confirmed C2 server IPs.",
        "filters": [{"field": "threat_type", "operator": "equals", "value": "c2"}]
    }
]


class AdvancedHuntingService:
    """Provides high-performance threat hunting workbench queries and template execution."""

    @classmethod
    async def get_hunt_templates(cls) -> List[Dict[str, Any]]:
        """Returns standard library of reusable threat hunting templates."""
        return HUNT_TEMPLATES

    @classmethod
    async def execute_hunt(
        cls,
        db: AsyncSession,
        tenant_id: str,
        target_entity: str,
        query_pattern: str,
        limit: int = 50,
        executed_by: str = "ANALYST"
    ) -> Dict[str, Any]:
        """
        Executes bounded hunting query across alerts, indicators, and security events.
        Measures execution latency and stores execution history.
        """
        t0 = time.perf_counter()
        bounded_limit = min(100, max(1, limit))
        pattern_norm = query_pattern.strip()

        # Query Alerts
        alert_stmt = (
            select(Alert)
            .where(
                or_(
                    Alert.source_ip.ilike(f"%{pattern_norm}%"),
                    Alert.destination_ip.ilike(f"%{pattern_norm}%"),
                    Alert.title.ilike(f"%{pattern_norm}%"),
                    Alert.attack_type.ilike(f"%{pattern_norm}%")
                )
            )
            .limit(bounded_limit)
        )
        alerts = list((await db.execute(alert_stmt)).scalars().all())

        # Query Threat Indicators
        ind_stmt = (
            select(ThreatIndicator)
            .where(
                or_(
                    ThreatIndicator.normalized_value.ilike(f"%{pattern_norm}%"),
                    ThreatIndicator.raw_value.ilike(f"%{pattern_norm}%"),
                    ThreatIndicator.source.ilike(f"%{pattern_norm}%")
                )
            )
            .limit(bounded_limit)
        )
        indicators = list((await db.execute(ind_stmt)).scalars().all())

        query_duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        total_results = len(alerts) + len(indicators)

        # Audit Execution Record
        execution = HuntingExecution(
            executed_by=executed_by,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            status="COMPLETED",
            result_count=total_results,
            query_duration_ms=int(query_duration_ms),
            parameters={"target_entity": target_entity, "query_pattern": pattern_norm}
        )
        db.add(execution)
        await db.flush()

        return {
            "execution_id": execution.id,
            "target_entity": target_entity,
            "query_pattern": pattern_norm,
            "total_matches": total_results,
            "query_duration_ms": query_duration_ms,
            "results": {
                "alerts": [
                    {
                        "id": a.id,
                        "title": a.title,
                        "source_ip": a.source_ip,
                        "destination_ip": a.destination_ip,
                        "severity": a.severity,
                        "attack_type": a.attack_type,
                        "timestamp": a.timestamp.isoformat() if a.timestamp else None
                    }
                    for a in alerts
                ],

                "indicators": [
                    {
                        "id": i.id,
                        "ioc_type": i.ioc_type,
                        "value": i.normalized_value,
                        "severity": i.severity,
                        "confidence": i.confidence,
                        "source": i.source
                    }
                    for i in indicators
                ]
            }
        }
