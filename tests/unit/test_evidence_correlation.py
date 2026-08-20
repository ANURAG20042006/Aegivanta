"""
tests/unit/test_evidence_correlation.py
=======================================
Phase 3.8 Unit Tests: Evidence Correlation Engine.
"""

import pytest
from backend.app.services.evidence_correlation_service import EvidenceCorrelationEngine


@pytest.mark.unit
@pytest.mark.asyncio
async def test_correlate_evidence_builds_graph_nodes_and_edges():
    """Verify EvidenceCorrelationEngine correlates seed entities into structured graph."""
    graph = await EvidenceCorrelationEngine.correlate_case_evidence(
        ips=["198.51.100.5", "10.0.0.2"],
        users=["compromised_user"],
        assets=["srv-prod-db01"],
        iocs=["198.51.100.5"]
    )

    assert graph["total_nodes"] >= 4
    assert any(n["id"] == "ip:198.51.100.5" for n in graph["nodes"])
    assert any(n["id"] == "user:compromised_user" for n in graph["nodes"])
    assert any(n["id"] == "asset:srv-prod-db01" for n in graph["nodes"])
    assert any(n["id"] == "ioc:198.51.100.5" for n in graph["nodes"])

    # Edge from IP to IOC
    assert any(e["source"] == "ip:198.51.100.5" and e["target"] == "ioc:198.51.100.5" for e in graph["edges"])
