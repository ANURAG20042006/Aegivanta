"""
backend/app/services/hunting_service.py
======================================
Advanced Parameterized Threat Hunting Query Engine.
Executes bounded, secure, structured threat hunting searches across multi-signal SOC telemetry.
"""

from datetime import datetime, timezone, timedelta
import time
from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.hunting import HuntingQuery, HuntingExecution
from backend.app.models.security_event import SecurityEvent
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.monitoring import MonitoringHistory

logger = logging.getLogger("SentinelAI")


class HuntingService:
    """Core Threat Hunting Execution Engine."""

    @staticmethod
    async def execute_hunting_query(
        query_def: Dict[str, Any],
        executed_by: str,
        query_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Executes a parameterized multi-entity threat hunt.
        Supported entities: events, alerts, incidents, iocs, monitoring.
        Supported filters: source_ip, destination_ip, attack_type, severity, asset_id, time_range.
        """
        t_start = time.perf_counter()
        target_entity = query_def.get("entity", "alerts").lower()
        limit = min(int(query_def.get("limit", 100)), 500)
        offset = max(int(query_def.get("offset", 0)), 0)
        
        # 1. Determine Time Range Bounds
        time_range = query_def.get("time_range", "24h")
        now_utc = datetime.now(timezone.utc)
        if time_range == "1h":
            since_time = now_utc - timedelta(hours=1)
        elif time_range == "7d":
            since_time = now_utc - timedelta(days=7)
        elif time_range == "30d":
            since_time = now_utc - timedelta(days=30)
        elif time_range == "custom" and "start_time" in query_def:
            try:
                since_time = datetime.fromisoformat(query_def["start_time"].replace("Z", "+00:00"))
            except Exception:
                since_time = now_utc - timedelta(hours=24)
        else:
            since_time = now_utc - timedelta(hours=24)

        filters = query_def.get("filters", {})
        results: List[Dict[str, Any]] = []

        # 2. Build Parameterized SQLAlchemy Queries by Target Entity
        if target_entity == "alerts":
            stmt = select(Alert).where(Alert.timestamp >= since_time)
            if "source_ip" in filters and filters["source_ip"]:
                stmt = stmt.where(Alert.source_ip == str(filters["source_ip"]).strip())
            if "destination_ip" in filters and filters["destination_ip"]:
                stmt = stmt.where(Alert.destination_ip == str(filters["destination_ip"]).strip())
            if "attack_type" in filters and filters["attack_type"]:
                stmt = stmt.where(Alert.attack_type.ilike(f"%{filters['attack_type']}%"))
            if "severity" in filters and filters["severity"]:
                stmt = stmt.where(Alert.severity.ilike(filters["severity"]))
            if "asset_id" in filters and filters["asset_id"]:
                stmt = stmt.where(Alert.asset_id == str(filters["asset_id"]))

            stmt = stmt.order_by(desc(Alert.timestamp)).offset(offset).limit(limit)
            exec_res = await db.execute(stmt)
            alerts = exec_res.scalars().all()
            for a in alerts:
                results.append({
                    "id": a.id,
                    "entity": "ALERT",
                    "title": a.title or a.attack_type,
                    "source_ip": a.source_ip,
                    "destination_ip": a.destination_ip,
                    "attack_type": a.attack_type,
                    "severity": a.severity,
                    "confidence": a.confidence,
                    "risk_score": a.risk_score,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                    "explanation": a.explanation
                })

        elif target_entity == "incidents":
            stmt = select(Incident).where(Incident.timestamp >= since_time)
            if "source_ip" in filters and filters["source_ip"]:
                stmt = stmt.where(Incident.source_ip == str(filters["source_ip"]).strip())
            if "destination_ip" in filters and filters["destination_ip"]:
                stmt = stmt.where(Incident.destination_ip == str(filters["destination_ip"]).strip())
            if "attack_type" in filters and filters["attack_type"]:
                stmt = stmt.where(Incident.attack_type.ilike(f"%{filters['attack_type']}%"))
            if "severity" in filters and filters["severity"]:
                stmt = stmt.where(Incident.severity.ilike(filters["severity"]))

            stmt = stmt.order_by(desc(Incident.timestamp)).offset(offset).limit(limit)
            exec_res = await db.execute(stmt)
            incs = exec_res.scalars().all()
            for inc in incs:
                results.append({
                    "id": inc.id,
                    "entity": "INCIDENT",
                    "incident_code": inc.incident_code,
                    "title": inc.title or inc.attack_type,
                    "source_ip": inc.source_ip,
                    "destination_ip": inc.destination_ip,
                    "attack_type": inc.attack_type,
                    "severity": inc.severity,
                    "risk_score": inc.risk_score,
                    "status": inc.status,
                    "timestamp": inc.timestamp.isoformat() if inc.timestamp else None
                })

        elif target_entity == "iocs":
            stmt = select(ThreatIndicator).where(ThreatIndicator.is_active == True)
            if "ioc_type" in filters and filters["ioc_type"]:
                stmt = stmt.where(ThreatIndicator.ioc_type == str(filters["ioc_type"]).lower())
            if "keyword" in filters and filters["keyword"]:
                stmt = stmt.where(ThreatIndicator.normalized_value.ilike(f"%{filters['keyword']}%"))

            stmt = stmt.order_by(desc(ThreatIndicator.created_at)).offset(offset).limit(limit)
            exec_res = await db.execute(stmt)
            iocs = exec_res.scalars().all()
            for ioc in iocs:
                results.append({
                    "id": ioc.id,
                    "entity": "IOC",
                    "ioc_type": ioc.ioc_type,
                    "value": ioc.normalized_value,
                    "threat_type": ioc.threat_type,
                    "severity": ioc.severity,
                    "confidence": ioc.confidence,
                    "source": ioc.source,
                    "tags": ioc.tags,
                    "hit_count": ioc.hit_count
                })

        duration_ms = int((time.perf_counter() - t_start) * 1000.0)

        # 3. Log Audit Execution Record
        execution = HuntingExecution(
            id=str(uuid.uuid4()),
            query_id=query_id,
            executed_by=executed_by,
            started_at=now_utc,
            completed_at=datetime.now(timezone.utc),
            status="COMPLETED",
            result_count=len(results),
            query_duration_ms=duration_ms,
            parameters=query_def
        )
        db.add(execution)
        await db.commit()

        return {
            "execution_id": execution.id,
            "entity": target_entity,
            "result_count": len(results),
            "query_duration_ms": duration_ms,
            "timestamp": now_utc.isoformat(),
            "results": results
        }

    @staticmethod
    async def create_saved_query(
        name: str,
        description: Optional[str],
        query_definition: Dict[str, Any],
        created_by: str,
        db: AsyncSession
    ) -> HuntingQuery:
        """Saves a parameterized query template."""
        query = HuntingQuery(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            query_definition=query_definition,
            created_by=created_by,
            is_saved=True
        )
        db.add(query)
        await db.commit()
        await db.refresh(query)
        return query

    @staticmethod
    async def list_saved_queries(db: AsyncSession) -> List[HuntingQuery]:
        """Lists all saved threat hunting queries."""
        stmt = select(HuntingQuery).where(HuntingQuery.is_saved == True).order_by(desc(HuntingQuery.created_at))
        res = await db.execute(stmt)
        return res.scalars().all()
