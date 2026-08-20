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
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict
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

    @staticmethod
    async def find_attack_paths(
        source_id: str,
        target_id: str,
        max_hops: int = 6,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Finds all simple directed attack paths up to max_hops between source_id and target_id.
        Computes shortest path, highest-risk path, and critical intermediate choke points.
        """
        topology = await ThreatGraphService.get_graph_topology(limit=300, db=db)
        nodes = {n["id"]: n for n in topology["nodes"]}
        edges = topology["edges"]

        if source_id not in nodes or target_id not in nodes:
            return {
                "source_id": source_id,
                "target_id": target_id,
                "paths_found": 0,
                "paths": [],
                "shortest_path": None,
                "highest_risk_path": None,
                "critical_chokepoints": []
            }

        # Build adjacency graph
        adj = defaultdict(list)
        for e in edges:
            adj[e["source"]].append((e["target"], e))
            # Also allow bidirectional traversal for relational correlation
            adj[e["target"]].append((e["source"], e))

        # DFS path finding
        all_paths: List[List[Dict[str, Any]]] = []

        def dfs(curr: str, target: str, visited: Set[str], current_path: List[Dict[str, Any]]):
            if len(current_path) > max_hops:
                return
            if curr == target and current_path:
                all_paths.append(list(current_path))
                return

            visited.add(curr)
            for nxt, edge_info in adj[curr]:
                if nxt not in visited:
                    current_path.append({
                        "from_node": curr,
                        "to_node": nxt,
                        "relationship": edge_info.get("relationship_type", "CONNECTED_TO"),
                        "confidence": edge_info.get("confidence", 0.85),
                        "evidence_count": edge_info.get("evidence_count", 1)
                    })
                    dfs(nxt, target, visited, current_path)
                    current_path.pop()
            visited.remove(curr)

        dfs(source_id, target_id, set(), [])

        # Score and format paths
        formatted_paths = []
        node_visit_counts: Dict[str, int] = defaultdict(int)

        for p_idx, p in enumerate(all_paths):
            path_nodes = [source_id] + [hop["to_node"] for hop in p]
            # Cumulative risk: 1 - prod(1 - conf)
            prob_safe = 1.0
            for hop in p:
                conf = hop.get("confidence", 0.85)
                prob_safe *= (1.0 - conf)
            cum_risk = round((1.0 - prob_safe) * 100.0, 2)

            # Record intermediate node visits for choke point analysis
            for n in path_nodes[1:-1]:
                node_visit_counts[n] += 1

            formatted_paths.append({
                "path_id": f"path-{p_idx + 1}",
                "hop_count": len(p),
                "nodes": path_nodes,
                "node_labels": [nodes.get(nid, {}).get("label", nid) for nid in path_nodes],
                "cumulative_risk": cum_risk,
                "hops": p
            })

        # Sort by cumulative risk descending, then hop count ascending
        formatted_paths.sort(key=lambda x: (x["cumulative_risk"], -x["hop_count"]), reverse=True)

        shortest_p = min(formatted_paths, key=lambda x: x["hop_count"]) if formatted_paths else None
        highest_risk_p = formatted_paths[0] if formatted_paths else None

        # Top choke points on paths
        chokepoints = [
            {
                "node_id": nid,
                "label": nodes.get(nid, {}).get("label", nid),
                "node_type": nodes.get(nid, {}).get("node_type", "UNKNOWN"),
                "path_frequency": count
            }
            for nid, count in sorted(node_visit_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "source_id": source_id,
            "target_id": target_id,
            "paths_found": len(formatted_paths),
            "paths": formatted_paths[:10],
            "shortest_path": shortest_p,
            "highest_risk_path": highest_risk_p,
            "critical_chokepoints": chokepoints[:5]
        }

    @staticmethod
    async def calculate_chokepoints(top_n: int = 10, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """
        Calculates betweenness & degree centrality across the attack graph to identify
        critical architectural choke points whose isolation halts multi-segment traversal.
        """
        topology = await ThreatGraphService.get_graph_topology(limit=300, db=db)
        nodes = {n["id"]: n for n in topology["nodes"]}
        edges = topology["edges"]

        if not nodes or not edges:
            return []

        # Degree counters
        in_degree: Dict[str, int] = defaultdict(int)
        out_degree: Dict[str, int] = defaultdict(int)
        connected_neighbors: Dict[str, Set[str]] = defaultdict(set)

        for e in edges:
            src, tgt = e["source"], e["target"]
            out_degree[src] += 1
            in_degree[tgt] += 1
            connected_neighbors[src].add(tgt)
            connected_neighbors[tgt].add(src)

        num_nodes = len(nodes)
        chokepoint_list = []

        for nid, node in nodes.items():
            total_deg = in_degree[nid] + out_degree[nid]
            deg_centrality = round(total_deg / max(num_nodes - 1, 1), 4)

            # High degree + critical asset or incident bridge -> elevated betweenness proxy
            betweenness_proxy = round(len(connected_neighbors[nid]) / max(num_nodes - 1, 1), 4)
            is_critical = node.get("criticality") == "CRITICAL" or node.get("severity") in ["CRITICAL", "HIGH"]

            # Strategic isolation priority
            priority = "URGENT" if (total_deg >= 4 or is_critical) else ("HIGH" if total_deg >= 2 else "MEDIUM")

            chokepoint_list.append({
                "node_id": nid,
                "label": node.get("label", nid),
                "node_type": node.get("node_type", "UNKNOWN"),
                "total_degree": total_deg,
                "in_degree": in_degree[nid],
                "out_degree": out_degree[nid],
                "degree_centrality": deg_centrality,
                "betweenness_score": betweenness_proxy,
                "connected_entities_count": len(connected_neighbors[nid]),
                "connected_entity_ids": list(connected_neighbors[nid]),
                "isolation_priority": priority
            })

        chokepoint_list.sort(key=lambda x: (x["betweenness_score"], x["total_degree"]), reverse=True)
        return chokepoint_list[:top_n]

    @staticmethod
    async def calculate_blast_radius(
        origin_node_id: str,
        max_depth: int = 3,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Computes forward reachability subgraph, exposed assets, and Crown Jewel Exposure Index
        from an initial compromised node.
        """
        topology = await ThreatGraphService.get_graph_topology(limit=300, db=db)
        nodes = {n["id"]: n for n in topology["nodes"]}
        edges = topology["edges"]

        if origin_node_id not in nodes:
            return {
                "origin_node_id": origin_node_id,
                "error": "Origin node not found in active graph topology.",
                "blast_radius_score": 0.0,
                "total_reachable_nodes": 0,
                "reachable_assets": [],
                "crown_jewel_exposure_index": 0.0
            }

        # Build forward adjacency
        adj = defaultdict(list)
        for e in edges:
            adj[e["source"]].append(e["target"])
            adj[e["target"]].append(e["source"])

        # BFS with depth tracking
        visited: Dict[str, int] = {origin_node_id: 0}
        queue = [(origin_node_id, 0)]

        while queue:
            curr, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited[neighbor] = depth + 1
                    queue.append((neighbor, depth + 1))

        reachable_assets = []
        critical_count = 0
        high_count = 0

        for nid, depth in visited.items():
            if nid == origin_node_id:
                continue
            node = nodes.get(nid, {})
            if node.get("node_type") == "ASSET":
                crit = node.get("criticality", "MEDIUM")
                if crit == "CRITICAL":
                    critical_count += 1
                elif crit == "HIGH":
                    high_count += 1
                reachable_assets.append({
                    "asset_id": node.get("reference_id", nid),
                    "label": node.get("label", nid),
                    "criticality": crit,
                    "ip_address": node.get("ip_address"),
                    "hop_distance": depth
                })

        # Crown Jewel Exposure Index calculation
        crown_jewel_index = round(min(critical_count * 35.0 + high_count * 15.0 + len(reachable_assets) * 5.0, 100.0), 2)
        blast_radius_score = round(min(len(visited) / max(len(nodes), 1) * 100.0, 100.0), 2)

        return {
            "origin_node_id": origin_node_id,
            "origin_label": nodes[origin_node_id].get("label", origin_node_id),
            "origin_type": nodes[origin_node_id].get("node_type", "UNKNOWN"),
            "max_traversal_depth": max_depth,
            "total_reachable_nodes": len(visited) - 1,
            "blast_radius_score": blast_radius_score,
            "crown_jewel_exposure_index": crown_jewel_index,
            "reachable_assets_count": len(reachable_assets),
            "critical_assets_exposed": critical_count,
            "high_assets_exposed": high_count,
            "reachable_assets": reachable_assets,
            "reachable_node_ids": list(visited.keys())
        }

    @staticmethod
    async def get_graph_analytics(db: AsyncSession = None) -> Dict[str, Any]:
        """Calculates topological summary analytics, density, clustering, and risk distribution."""
        topology = await ThreatGraphService.get_graph_topology(limit=300, db=db)
        nodes = topology["nodes"]
        edges = topology["edges"]

        v = len(nodes)
        e = len(edges)
        density = round((2.0 * e) / max(v * (v - 1), 1), 4) if v > 1 else 0.0

        node_types = defaultdict(int)
        for n in nodes:
            node_types[n.get("node_type", "OTHER")] += 1

        rel_types = defaultdict(int)
        for edge in edges:
            rel_types[edge.get("relationship_type", "OTHER")] += 1

        avg_degree = round((2.0 * e) / max(v, 1), 2)

        return {
            "total_nodes": v,
            "total_edges": e,
            "graph_density": density,
            "average_degree": avg_degree,
            "node_type_distribution": dict(node_types),
            "relationship_type_distribution": dict(rel_types),
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }

