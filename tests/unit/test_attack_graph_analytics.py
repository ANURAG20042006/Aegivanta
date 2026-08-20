"""
tests/unit/test_attack_graph_analytics.py
=========================================
Phase 3.5 Unit Tests: Attack Graph Analytics, Path Finding, Chokepoints & Blast Radius.
Verifies multi-hop path search, betweenness/degree centrality, and crown jewel exposure index.
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.app.services.threat_graph_service import ThreatGraphService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_attack_paths_mock_topology():
    """Verify attack path search finds multi-hop paths and calculates cumulative risk."""
    mock_topology = {
        "total_nodes": 4,
        "total_edges": 3,
        "nodes": [
            {"id": "asset-1", "label": "Web Gateway", "node_type": "ASSET"},
            {"id": "inc-1", "label": "INC-001", "node_type": "INCIDENT"},
            {"id": "asset-2", "label": "App Server", "node_type": "ASSET"},
            {"id": "asset-3", "label": "DB Server", "node_type": "ASSET"}
        ],
        "edges": [
            {"source": "asset-1", "target": "inc-1", "relationship_type": "TARGETS", "confidence": 0.90},
            {"source": "inc-1", "target": "asset-2", "relationship_type": "TARGETS", "confidence": 0.85},
            {"source": "asset-2", "target": "asset-3", "relationship_type": "COMMUNICATES_WITH", "confidence": 0.95}
        ]
    }

    with patch.object(ThreatGraphService, "get_graph_topology", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_topology

        res = await ThreatGraphService.find_attack_paths("asset-1", "asset-3", max_hops=5)

        assert res["paths_found"] >= 1
        assert res["shortest_path"] is not None
        assert res["shortest_path"]["hop_count"] == 3
        assert res["shortest_path"]["nodes"] == ["asset-1", "inc-1", "asset-2", "asset-3"]
        assert res["highest_risk_path"] is not None
        assert res["highest_risk_path"]["cumulative_risk"] > 90.0
        assert len(res["critical_chokepoints"]) >= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_chokepoints_centrality():
    """Verify centrality ranking identifies bridge nodes with highest connectivity."""
    mock_topology = {
        "total_nodes": 4,
        "total_edges": 3,
        "nodes": [
            {"id": "node-A", "label": "Host A", "node_type": "ASSET", "criticality": "LOW"},
            {"id": "node-B", "label": "Bridge Switch", "node_type": "ASSET", "criticality": "CRITICAL"},
            {"id": "node-C", "label": "Host C", "node_type": "ASSET", "criticality": "MEDIUM"},
            {"id": "node-D", "label": "Host D", "node_type": "ASSET", "criticality": "MEDIUM"}
        ],
        "edges": [
            {"source": "node-A", "target": "node-B"},
            {"source": "node-B", "target": "node-C"},
            {"source": "node-B", "target": "node-D"}
        ]
    }

    with patch.object(ThreatGraphService, "get_graph_topology", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_topology

        chokepoints = await ThreatGraphService.calculate_chokepoints(top_n=5)

        assert len(chokepoints) == 4
        # node-B should be ranked first as the bridge connecting A, C, and D
        top_node = chokepoints[0]
        assert top_node["node_id"] == "node-B"
        assert top_node["total_degree"] == 3
        assert top_node["isolation_priority"] in ["URGENT", "HIGH"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_blast_radius_reachability():
    """Verify forward reachability computation and Crown Jewel Exposure Index."""
    mock_topology = {
        "total_nodes": 4,
        "total_edges": 3,
        "nodes": [
            {"id": "asset-origin", "label": "Compromised Host", "node_type": "ASSET", "criticality": "LOW"},
            {"id": "asset-db", "label": "Core DB", "node_type": "ASSET", "criticality": "CRITICAL", "reference_id": "a-db"},
            {"id": "asset-auth", "label": "Auth Server", "node_type": "ASSET", "criticality": "HIGH", "reference_id": "a-auth"},
            {"id": "ioc-c2", "label": "C2 Server", "node_type": "IOC"}
        ],
        "edges": [
            {"source": "asset-origin", "target": "asset-db"},
            {"source": "asset-origin", "target": "asset-auth"},
            {"source": "asset-origin", "target": "ioc-c2"}
        ]
    }

    with patch.object(ThreatGraphService, "get_graph_topology", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_topology

        res = await ThreatGraphService.calculate_blast_radius("asset-origin", max_depth=2)

        assert res["origin_node_id"] == "asset-origin"
        assert res["total_reachable_nodes"] == 3
        assert res["critical_assets_exposed"] == 1
        assert res["high_assets_exposed"] == 1
        assert res["crown_jewel_exposure_index"] > 50.0
        assert len(res["reachable_assets"]) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_graph_analytics():
    """Verify calculation of topological summary metrics and density."""
    mock_topology = {
        "total_nodes": 3,
        "total_edges": 2,
        "nodes": [
            {"id": "n1", "node_type": "ASSET"},
            {"id": "n2", "node_type": "INCIDENT"},
            {"id": "n3", "node_type": "IOC"}
        ],
        "edges": [
            {"source": "n1", "target": "n2", "relationship_type": "TARGETS"},
            {"source": "n2", "target": "n3", "relationship_type": "INDICATES"}
        ]
    }

    with patch.object(ThreatGraphService, "get_graph_topology", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_topology

        res = await ThreatGraphService.get_graph_analytics()

        assert res["total_nodes"] == 3
        assert res["total_edges"] == 2
        assert res["graph_density"] > 0.0
        assert res["average_degree"] > 0.0
        assert res["node_type_distribution"]["ASSET"] == 1
        assert res["relationship_type_distribution"]["TARGETS"] == 1
