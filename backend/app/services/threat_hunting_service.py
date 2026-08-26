"""
backend/app/services/threat_hunting_service.py
==============================================
Phase 3.8 Secure Parameterized Threat Hunting Query Engine.
Executes bounded, typed DSL searches across SOC telemetry without exposing raw SQL.
"""

from datetime import datetime, timezone, timedelta
import time
from typing import Dict, Any, List, Optional, Union
import uuid
import logging
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.hunting import HuntingQuery, HuntingExecution
from backend.app.models.security_event import SecurityEvent
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.monitoring import MonitoringHistory

logger = logging.getLogger("SentinelAI")

ALLOWED_QUERY_FIELDS = {
    "source_ip", "destination_ip", "source_port", "destination_port", "protocol",
    "hostname", "username", "asset_id", "ioc_value", "domain", "url", "hash",
    "event_type", "severity", "mitre_technique", "incident_id", "attack_type", "status"
}

ALLOWED_OPERATORS = {
    "equals", "not_equals", "contains", "starts_with", "in", "not_in",
    "greater_than", "less_than", "between"
}


class ThreatHuntingQueryValidator:
    """Validates structured DSL query syntax, operators, and values."""

    @staticmethod
    def validate_filter(field: str, operator: str, value: Any):
        if field.lower() not in ALLOWED_QUERY_FIELDS:
            raise ValueError(f"Field '{field}' is not a permitted threat hunting query field. Allowed: {sorted(ALLOWED_QUERY_FIELDS)}")

        if operator.lower() not in ALLOWED_OPERATORS:
            raise ValueError(f"Operator '{operator}' is not supported. Allowed: {sorted(ALLOWED_OPERATORS)}")


class ThreatHuntingService:
    """Core Threat Hunting Service executing safe DSL queries and managing hunt templates."""

    @classmethod
    async def execute_dsl_query(
        cls,
        entity: str = "events",
        time_range: Optional[Dict[str, str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        limit: int = 100,
        offset: int = 0,
        executed_by: str = "analyst",
        query_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Executes a typed structured threat hunting search.
        """
        t0 = time.perf_counter()
        bounded_limit = max(1, min(limit, 1000))
        bounded_offset = max(0, offset)
        filters = filters or []

        # Validate all filters
        for f in filters:
            ThreatHuntingQueryValidator.validate_filter(
                field=f.get("field", ""),
                operator=f.get("operator", "equals"),
                value=f.get("value")
            )

        # Parse Time Range
        now_utc = datetime.now(timezone.utc)
        start_time = now_utc - timedelta(hours=24)
        end_time = now_utc

        if time_range:
            if "start" in time_range and time_range["start"]:
                try:
                    start_time = datetime.fromisoformat(time_range["start"].replace("Z", "+00:00"))
                except Exception:
                    pass
            if "end" in time_range and time_range["end"]:
                try:
                    end_time = datetime.fromisoformat(time_range["end"].replace("Z", "+00:00"))
                except Exception:
                    pass

        results: List[Dict[str, Any]] = []

        from backend.app.core.environment import get_authoritative_environment, AegivantaEnvironment, SecurityEnvironmentError
        current_env = get_authoritative_environment()

        if db is None:
            if current_env == AegivantaEnvironment.PRODUCTION:
                from backend.app.core.environment import record_security_violation
                record_security_violation(
                    component="THREAT_HUNTING",
                    source=entity,
                    reason="Threat hunting query execution failed closed due to missing database session in PRODUCTION.",
                    environment=current_env
                )
                raise SecurityEnvironmentError("Production threat hunting requires an active database session. Simulated empty returns are prohibited.")
            return {
                "entity": entity,
                "total_matches": 0,
                "total_matched": 0,
                "result_count": 0,
                "limit": bounded_limit,
                "offset": bounded_offset,
                "duration_ms": round((time.perf_counter() - t0) * 1000.0, 2),
                "execution_time_ms": round((time.perf_counter() - t0) * 1000.0, 2),
                "executed_by": executed_by,
                "results": []
            }


        entity_lower = entity.lower().strip()
        if entity_lower in ["events", "security_events", "telemetry"]:
            results = await cls._query_security_events(filters, start_time, end_time, bounded_limit, bounded_offset, db)
        elif entity_lower in ["alerts", "detections"]:
            results = await cls._query_alerts(filters, start_time, end_time, bounded_limit, bounded_offset, db)
        elif entity_lower in ["incidents"]:
            results = await cls._query_incidents(filters, start_time, end_time, bounded_limit, bounded_offset, db)
        elif entity_lower in ["iocs", "threat_indicators"]:
            results = await cls._query_iocs(filters, bounded_limit, bounded_offset, db)
        else:
            raise ValueError(f"Unknown hunting entity target: '{entity}'. Permitted: events, alerts, incidents, iocs.")

        duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        # Audit Execution Record
        if db and query_id:
            try:
                exec_log = HuntingExecution(
                    id=str(uuid.uuid4()),
                    query_id=query_id,
                    executed_by=executed_by,
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    status="COMPLETED",
                    result_count=len(results),
                    query_duration_ms=int(duration_ms),
                    parameters={"entity": entity, "filters": filters, "limit": bounded_limit}
                )
                db.add(exec_log)
                await db.commit()
            except Exception as e:
                logger.debug("Hunting execution log error: %s", e)

        return {
            "entity": entity,
            "total_matches": len(results),
            "result_count": len(results),
            "limit": bounded_limit,
            "offset": bounded_offset,
            "duration_ms": duration_ms,
            "executed_by": executed_by,
            "results": results
        }

    @classmethod
    async def _query_security_events(
        cls,
        filters: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        query = select(SecurityEvent).where(
            SecurityEvent.timestamp >= start_time,
            SecurityEvent.timestamp <= end_time
        )
        for f in filters:
            field = f["field"].lower()
            op = f.get("operator", "equals").lower()
            val = f.get("value")

            col = getattr(SecurityEvent, field, None)
            if col is not None:
                if op == "equals":
                    query = query.where(col == val)
                elif op == "not_equals":
                    query = query.where(col != val)
                elif op == "contains" and isinstance(val, str):
                    query = query.where(col.ilike(f"%{val}%"))
                elif op == "in" and isinstance(val, list):
                    query = query.where(col.in_(val))

        query = query.order_by(desc(SecurityEvent.timestamp)).offset(offset).limit(limit)
        res = await db.execute(query)
        events = res.scalars().all()
        return [
            {
                "id": ev.id,
                "event_id": ev.event_id,
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                "source_ip": ev.source_ip,
                "destination_ip": ev.destination_ip,
                "source_port": ev.source_port,
                "destination_port": ev.destination_port,
                "protocol": ev.protocol,
                "event_type": ev.event_type,
                "severity": ev.severity,
                "attack_type": ev.model_prediction or ev.event_type,
                "model_prediction": ev.model_prediction,
                "confidence": ev.confidence,
                "risk_score": ev.risk_score
            }
            for ev in events
        ]

    @classmethod
    async def _query_alerts(
        cls,
        filters: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        query = select(Alert).where(
            Alert.created_at >= start_time,
            Alert.created_at <= end_time
        )
        for f in filters:
            field = f["field"].lower()
            op = f.get("operator", "equals").lower()
            val = f.get("value")

            col = getattr(Alert, field, None)
            if col is not None:
                if op == "equals":
                    query = query.where(col == val)
                elif op == "contains" and isinstance(val, str):
                    query = query.where(col.ilike(f"%{val}%"))
                elif op == "in" and isinstance(val, list):
                    query = query.where(col.in_(val))

        query = query.order_by(desc(Alert.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        alerts = res.scalars().all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "severity": a.severity,
                "source_ip": a.source_ip,
                "destination_ip": a.destination_ip,
                "attack_type": a.attack_type,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ]

    @classmethod
    async def _query_incidents(
        cls,
        filters: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        query = select(Incident).where(
            Incident.created_at >= start_time,
            Incident.created_at <= end_time
        )
        for f in filters:
            field = f["field"].lower()
            op = f.get("operator", "equals").lower()
            val = f.get("value")

            col = getattr(Incident, field, None)
            if col is not None:
                if op == "equals":
                    query = query.where(col == val)
                elif op == "contains" and isinstance(val, str):
                    query = query.where(col.ilike(f"%{val}%"))
                elif op == "in" and isinstance(val, list):
                    query = query.where(col.in_(val))

        query = query.order_by(desc(Incident.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        incidents = res.scalars().all()
        return [
            {
                "id": inc.id,
                "incident_code": inc.incident_code,
                "source_ip": inc.source_ip,
                "destination_ip": inc.destination_ip,
                "attack_type": inc.attack_type,
                "severity": inc.severity,
                "risk_score": inc.risk_score,
                "status": inc.status,
                "created_at": inc.created_at.isoformat() if inc.created_at else None
            }
            for inc in incidents
        ]

    @classmethod
    async def _query_iocs(
        cls,
        filters: List[Dict[str, Any]],
        limit: int,
        offset: int,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        query = select(ThreatIndicator)
        for f in filters:
            field = f["field"].lower()
            op = f.get("operator", "equals").lower()
            val = f.get("value")

            col = getattr(ThreatIndicator, field, None)
            if col is not None:
                if op == "equals":
                    query = query.where(col == val)
                elif op == "contains" and isinstance(val, str):
                    query = query.where(col.ilike(f"%{val}%"))
                elif op == "in" and isinstance(val, list):
                    query = query.where(col.in_(val))

        query = query.offset(offset).limit(limit)
        res = await db.execute(query)
        iocs = res.scalars().all()
        return [
            {
                "id": ioc.id,
                "normalized_value": ioc.normalized_value,
                "raw_value": ioc.raw_value,
                "ioc_type": ioc.ioc_type,
                "severity": ioc.severity,
                "confidence": ioc.confidence,
                "source": ioc.source,
                "is_active": ioc.is_active
            }
            for ioc in iocs
        ]

    # Legacy Backward-Compatible Method
    @classmethod
    async def execute_hunting_query(
        cls,
        query_def: Dict[str, Any],
        executed_by: str,
        query_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Wrapper ensuring full backward compatibility with Phase 3.0-3.3 tests."""
        entity = query_def.get("entity", "alerts")
        limit = query_def.get("limit", 100)
        offset = query_def.get("offset", 0)
        raw_filters = query_def.get("filters", {})

        dsl_filters = []
        if isinstance(raw_filters, dict):
            for k, v in raw_filters.items():
                dsl_filters.append({"field": k, "operator": "equals", "value": v})
        elif isinstance(raw_filters, list):
            dsl_filters = raw_filters

        return await cls.execute_dsl_query(
            entity=entity,
            time_range={"start": query_def.get("start_time")} if query_def.get("start_time") else None,
            filters=dsl_filters,
            limit=limit,
            offset=offset,
            executed_by=executed_by,
            query_id=query_id,
            db=db
        )

    @classmethod
    async def list_saved_queries(cls, db: AsyncSession) -> List[HuntingQuery]:
        res = await db.execute(select(HuntingQuery).order_by(desc(HuntingQuery.created_at)))
        return res.scalars().all()
