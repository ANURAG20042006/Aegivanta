"""
tests/unit/test_phase3_threat_graph.py
======================================
Unit tests for Threat Intelligence Graph Topology and Evidence Verification.
"""

import pytest
from backend.app.database import AsyncSessionFactory
from backend.app.services.threat_graph_service import ThreatGraphService


@pytest.mark.asyncio
async def test_threat_graph_topology_generation():
    """Verify Threat Graph builds nodes and evidence-backed edges."""
    async with AsyncSessionFactory() as db:
        graph = await ThreatGraphService.get_graph_topology(limit=50, db=db)
        assert "nodes" in graph
        assert "edges" in graph
        assert isinstance(graph["nodes"], list)
        assert isinstance(graph["edges"], list)
        
        # Verify edge evidence invariant
        for edge in graph["edges"]:
            assert edge["evidence_count"] >= 1
            assert edge["confidence"] > 0.0
