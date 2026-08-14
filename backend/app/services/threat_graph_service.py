"""
backend/app/services/threat_graph_service.py
============================================
Threat Intelligence Graph Engine.
Constructs multi-entity relationship topologies (Assets, Alerts, IOCs, Incidents, Techniques)
with strict evidence verification and provenance linking.
"""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.threat_graph import ThreatGraphNode, ThreatGraphEdge
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.investigation import Investigation

logger = logging.getLogger("SentinelAI")


class ThreatGraphService:
    """Constructs and queries the SOC Threat Intelligence Graph."""

    @staticmethod
    async def get_graph_topology(limit: int = 150, db: AsyncSession = None) -> Dict[str, Any]:
        """
        Builds graph topology by aggregating live SOC entities:
        Assets -> Incidents -> Alerts -> IOCs -> MITRE ATT&CK Techniques.
        """
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        node_id_map: Dict[str, str] = {}

        # 1. Add Asset Nodes
        res_assets = await db.execute(select(ProtectedAsset).limit(20))
        assets = res_assets.scalars().all()
        for a in assets:
            nid = f"asset-{a.id}"
            node_id_map[f"asset_{a.id}"] = nid
            nodes.append({
                "id": nid,
                "node_type": "ASSET",
                "label": a.name,
                "reference_id": a.id,
                "criticality": a.criticality,
                "ip_address": a.ip_address,
                "status": a.status
            })

        # 2. Add Incident Nodes & Asset->Incident Edges
        res_inc = await db.execute(select(Incident).order_by(desc(Incident.timestamp)).limit(25))
        incidents = res_inc.scalars().all()
        for inc in incidents:
            nid = f"inc-{inc.id}"
            node_id_map[f"inc_{inc.id}"] = nid
            nodes.append({
                "id": nid,
                "node_type": "INCIDENT",
                "label": inc.incident_code or f"INC-{inc.id[:8]}",
                "reference_id": inc.id,
                "attack_type": inc.attack_type,
                "severity": inc.severity,
                "risk_score": inc.risk_score,
                "status": inc.status
            })

            # Edge from Incident to Asset (if matched)
            if inc.asset_id and f"asset_{inc.asset_id}" in node_id_map:
                edges.append({
                    "id": f"edge-inc-asset-{inc.id}",
                    "source": nid,
                    "target": node_id_map[f"asset_{inc.asset_id}"],
                    "relationship_type": "TARGETS",
                    "confidence": 0.95,
                    "evidence_count": inc.alert_count or 1
                })

        # 3. Add IOC Nodes & IOC->Incident Edges
        res_iocs = await db.execute(select(ThreatIndicator).where(ThreatIndicator.is_active == True).limit(20))
        iocs = res_iocs.scalars().all()
        for ioc in iocs:
            nid = f"ioc-{ioc.id}"
            nodes.append({
                "id": nid,
                "node_type": "IOC",
                "label": f"{ioc.ioc_type.upper()}: {ioc.normalized_value}",
                "reference_id": ioc.id,
                "threat_type": ioc.threat_type,
                "severity": ioc.severity,
                "confidence": ioc.confidence
            })

            # Check if any incident matches IOC IP
            for inc in incidents:
                if inc.source_ip == ioc.normalized_value or inc.destination_ip == ioc.normalized_value:
                    edges.append({
                        "id": f"edge-ioc-inc-{ioc.id}-{inc.id}",
                        "source": nid,
                        "target": f"inc-{inc.id}",
                        "relationship_type": "INDICATES",
                        "confidence": ioc.confidence or 0.90,
                        "evidence_count": ioc.hit_count or 1
                    })

        # 4. Add ATT&CK Technique Nodes from Investigations
        res_inv = await db.execute(select(Investigation).limit(15))
        invs = res_inv.scalars().all()
        technique_nodes_created: Dict[str, str] = {}
        
        for inv in invs:
            stage = inv.attack_chain_stage or "RECONNAISSANCE"
            tech_nid = f"tech-{stage}"
            if stage not in technique_nodes_created:
                technique_nodes_created[stage] = tech_nid
                nodes.append({
                    "id": tech_nid,
                    "node_type": "TECHNIQUE",
                    "label": f"MITRE {stage}",
                    "reference_id": stage,
                    "stage": stage
                })

            if f"inc_{inv.incident_id}" in node_id_map:
                edges.append({
                    "id": f"edge-inc-tech-{inv.incident_id}-{stage}",
                    "source": node_id_map[f"inc_{inv.incident_id}"],
                    "target": tech_nid,
                    "relationship_type": "EXECUTES",
                    "confidence": inv.confidence_score or 0.85,
                    "evidence_count": len(inv.findings or {}) or 1
                })

        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    async def get_node_evidence(node_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Fetches underlying evidence records supporting a given graph node."""
        if node_id.startswith("asset-"):
            aid = node_id.replace("asset-", "")
            res = await db.execute(select(ProtectedAsset).where(ProtectedAsset.id == aid))
            asset = res.scalar_one_or_none()
            return {"node_id": node_id, "entity_type": "ASSET", "data": asset.__dict__ if asset else None}
        elif node_id.startswith("inc-"):
            iid = node_id.replace("inc-", "")
            res = await db.execute(select(Incident).where(Incident.id == iid))
            inc = res.scalar_one_or_none()
            return {"node_id": node_id, "entity_type": "INCIDENT", "data": inc.__dict__ if inc else None}
        elif node_id.startswith("ioc-"):
            ioc_id = node_id.replace("ioc-", "")
            res = await db.execute(select(ThreatIndicator).where(ThreatIndicator.id == ioc_id))
            ioc = res.scalar_one_or_none()
            return {"node_id": node_id, "entity_type": "IOC", "data": ioc.__dict__ if ioc else None}
        
        return {"node_id": node_id, "entity_type": "GENERIC", "data": {}}
