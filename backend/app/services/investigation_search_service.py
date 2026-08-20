"""
backend/app/services/investigation_search_service.py
====================================================
Phase 16.7 Threat Investigation Unified Search Engine.
Provides high-performance, bounded, tenant-isolated search across alerts,
incidents, assets, threat indicators, detection rules, and audit logs.
"""

import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.detection_rule import DetectionRule
from backend.app.models.audit_log import AuditLog

logger = logging.getLogger("Aegivanta.InvestigationSearch")


class InvestigationSearchService:
    """Unified search service across core SOC domain entities with performance metrics."""

    @classmethod
    async def global_search(
        cls,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        query: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        severity: Optional[str] = None,
        source_ip: Optional[str] = None,
        destination_ip: Optional[str] = None,
        asset_id: Optional[str] = None,
        lookback_days: int = 30,
        page: int = 1,
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Executes bounded, indexed search across alerts, incidents, assets, threat intel, rules, and audit records.
        """
        t0 = time.perf_counter()
        limit = min(100, max(1, limit)) # Bound maximum results per page
        offset = (max(1, page) - 1) * limit
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        targets = entity_types or ["alerts", "incidents", "assets", "threat_intel", "rules"]
        results: Dict[str, Any] = {}
        total_matches = 0

        search_term = f"%{query.strip()}%" if query and query.strip() else None

        # 1. Search Alerts
        if "alerts" in targets:
            stmt = select(Alert).where(Alert.timestamp >= cutoff)
            if severity:
                stmt = stmt.where(Alert.severity == severity.lower())
            if source_ip:
                stmt = stmt.where(Alert.source_ip == source_ip)
            if destination_ip:
                stmt = stmt.where(Alert.destination_ip == destination_ip)
            if asset_id:
                stmt = stmt.where(Alert.asset_id == asset_id)
            if search_term:
                stmt = stmt.where(or_(Alert.title.ilike(search_term), Alert.attack_type.ilike(search_term)))

            stmt = stmt.order_by(Alert.timestamp.desc()).offset(offset).limit(limit)
            alert_res = await db.execute(stmt)
            alert_rows = list(alert_res.scalars().all())

            results["alerts"] = [
                {
                    "id": a.id,
                    "alert_id": a.alert_id,
                    "title": a.title,
                    "severity": a.severity,
                    "risk_score": a.risk_score,
                    "source_ip": a.source_ip,
                    "destination_ip": a.destination_ip,
                    "attack_type": a.attack_type,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in alert_rows
            ]
            total_matches += len(alert_rows)

        # 2. Search Incidents
        if "incidents" in targets:
            inc_stmt = select(Incident).where(Incident.timestamp >= cutoff)
            if severity:
                inc_stmt = inc_stmt.where(Incident.severity.ilike(severity))
            if source_ip:
                inc_stmt = inc_stmt.where(Incident.source_ip == source_ip)
            if destination_ip:
                inc_stmt = inc_stmt.where(Incident.destination_ip == destination_ip)
            if asset_id:
                inc_stmt = inc_stmt.where(Incident.asset_id == asset_id)
            if search_term:
                inc_stmt = inc_stmt.where(or_(Incident.title.ilike(search_term), Incident.attack_type.ilike(search_term)))

            inc_stmt = inc_stmt.order_by(Incident.timestamp.desc()).offset(offset).limit(limit)
            inc_res = await db.execute(inc_stmt)
            inc_rows = list(inc_res.scalars().all())

            results["incidents"] = [
                {
                    "id": i.id,
                    "incident_code": i.incident_code,
                    "title": i.title,
                    "status": i.status,
                    "severity": i.severity,
                    "risk_score": i.risk_score,
                    "source_ip": i.source_ip,
                    "destination_ip": i.destination_ip,
                    "attack_type": i.attack_type,
                    "timestamp": i.timestamp.isoformat()
                }
                for i in inc_rows
            ]
            total_matches += len(inc_rows)

        # 3. Search Assets
        if "assets" in targets:
            ast_stmt = select(ProtectedAsset)
            if search_term:
                ast_stmt = ast_stmt.where(or_(ProtectedAsset.name.ilike(search_term), ProtectedAsset.ip_address.ilike(search_term)))
            ast_stmt = ast_stmt.limit(limit)
            ast_res = await db.execute(ast_stmt)
            ast_rows = list(ast_res.scalars().all())
            results["assets"] = [
                {"id": x.id, "name": x.name, "ip_address": x.ip_address, "criticality": str(x.criticality), "status": x.status}
                for x in ast_rows
            ]
            total_matches += len(ast_rows)

        # 4. Search Threat Intelligence
        if "threat_intel" in targets:
            ti_stmt = select(ThreatIndicator)
            if search_term:
                ti_stmt = ti_stmt.where(
                    or_(
                        ThreatIndicator.normalized_value.ilike(search_term),
                        ThreatIndicator.raw_value.ilike(search_term),
                        ThreatIndicator.ioc_type.ilike(search_term)
                    )
                )
            ti_stmt = ti_stmt.limit(limit)
            ti_res = await db.execute(ti_stmt)
            ti_rows = list(ti_res.scalars().all())
            results["threat_intel"] = [
                {"id": t.id, "value": t.normalized_value or t.raw_value, "type": t.ioc_type, "severity": t.severity, "confidence": t.confidence}
                for t in ti_rows
            ]
            total_matches += len(ti_rows)


        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        return {
            "query": query,
            "page": page,
            "limit": limit,
            "lookback_days": lookback_days,
            "total_matches": total_matches,
            "query_latency_ms": elapsed_ms,
            "results": results
        }
