"""
backend/app/services/evidence_correlation_service.py
====================================================
Phase 3.8 Evidence Correlation Engine.
Constructs empirical, traceable evidence relationship graphs across SOC entities.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timezone
import uuid
import logging
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.security_event import SecurityEvent
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.response import ResponseActionRecord

logger = logging.getLogger("SentinelAI")


class EvidenceCorrelationEngine:
    """Discovers and correlates traceable forensic relationships across entities."""

    @classmethod
    async def correlate_case_evidence(
        cls,
        incident_ids: Optional[List[str]] = None,
        ips: Optional[List[str]] = None,
        users: Optional[List[str]] = None,
        assets: Optional[List[str]] = None,
        iocs: Optional[List[str]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive evidence graph connecting all provided entity seeds.
        """
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []

        incident_ids = incident_ids or []
        ips = set(ips or [])
        users = set(users or [])
        assets = set(assets or [])
        iocs = set(iocs or [])

        def add_node(node_id: str, label: str, node_type: str, metadata: Optional[Dict[str, Any]] = None):
            if node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "metadata": metadata or {}
                }

        def add_edge(src: str, dst: str, rel_type: str, confidence: float = 0.90, evidence_ref: Optional[str] = None):
            edges.append({
                "source": src,
                "target": dst,
                "relationship": rel_type,
                "confidence": confidence,
                "evidence_ref": evidence_ref
            })

        # 1. Expand Incidents
        if db and incident_ids:
            res_inc = await db.execute(select(Incident).where(Incident.id.in_(incident_ids)))
            for inc in res_inc.scalars().all():
                inc_node_id = f"inc:{inc.id}"
                add_node(inc_node_id, inc.incident_code or inc.id, "INCIDENT", {
                    "severity": inc.severity, "risk_score": inc.risk_score, "attack_type": inc.attack_type
                })

                if inc.source_ip:
                    ips.add(inc.source_ip)
                    src_node = f"ip:{inc.source_ip}"
                    add_node(src_node, inc.source_ip, "IP")
                    add_edge(src_node, inc_node_id, "TRIGGERED_INCIDENT", confidence=0.95, evidence_ref=inc.id)

                if inc.destination_ip:
                    ips.add(inc.destination_ip)
                    dst_node = f"ip:{inc.destination_ip}"
                    add_node(dst_node, inc.destination_ip, "IP")
                    add_edge(inc_node_id, dst_node, "TARGETED_HOST", confidence=0.90, evidence_ref=inc.id)

        # 2. Add IP and IOC nodes
        for ip in ips:
            ip_node = f"ip:{ip}"
            add_node(ip_node, ip, "IP")

        for ioc in iocs:
            ioc_node = f"ioc:{ioc}"
            add_node(ioc_node, ioc, "IOC", {"reputation": "MALICIOUS"})
            if ioc in ips:
                add_edge(f"ip:{ioc}", ioc_node, "MATCHED_THREAT_INTEL", confidence=0.98, evidence_ref=ioc)

        for usr in users:
            usr_node = f"user:{usr}"
            add_node(usr_node, usr, "USER")

        for ast in assets:
            ast_node = f"asset:{ast}"
            add_node(ast_node, ast, "ASSET")

        # 3. Query Response Actions
        if db and incident_ids:
            res_act = await db.execute(select(ResponseActionRecord).where(ResponseActionRecord.incident_id.in_(incident_ids)))
            for act in res_act.scalars().all():
                act_node_id = f"action:{act.id}"
                add_node(act_node_id, act.action_type, "RESPONSE_ACTION", {
                    "status": act.status, "target": act.target_entity
                })
                add_edge(f"inc:{act.incident_id}", act_node_id, "TRIGGERED_REMEDIATION", confidence=1.0, evidence_ref=act.id)
                if act.target_type == "IP" and act.target_entity in ips:
                    add_edge(act_node_id, f"ip:{act.target_entity}", "CONTAINED_TARGET", confidence=1.0)

        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": list(nodes.values()),
            "edges": edges,
            "correlated_at": datetime.now(timezone.utc).isoformat()
        }
