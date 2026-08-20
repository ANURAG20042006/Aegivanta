"""
tests/unit/test_phase16_investigation_search.py
===============================================
Phase 16.7 Unit Tests: Unified Multi-Entity Threat Search.
"""

import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.services.investigation_search_service import InvestigationSearchService


@pytest.mark.asyncio
async def test_unified_search_across_entities():
    """Validates multi-target search across alerts and incidents with pagination and metrics."""
    await init_db()
    async with AsyncSessionFactory() as db:
        # Seed test entities
        alert = Alert(
            title="Searchable Malicious Probe",
            severity="high",
            confidence=0.88,
            risk_score=75.0,
            source_ip="192.0.2.45",
            destination_ip="10.0.0.99",
            attack_type="Botnet",
            source="ML_ENGINE:CatBoost"
        )
        incident = Incident(
            title="Searchable Incident Target",
            source_ip="192.0.2.45",
            destination_ip="10.0.0.99",
            source_port=5555,
            destination_port=8080,
            protocol="TCP",
            packet_length=512,
            attack_type="Botnet",
            is_malicious=True,
            severity="High",
            status="TRIAGED"
        )
        db.add_all([alert, incident])
        await db.flush()

        res = await InvestigationSearchService.global_search(
            db=db,
            query="Searchable",
            entity_types=["alerts", "incidents"],
            page=1,
            limit=10
        )

        assert "results" in res
        assert "query_latency_ms" in res
        assert res["query_latency_ms"] >= 0.0
        assert len(res["results"].get("alerts", [])) >= 1
        assert len(res["results"].get("incidents", [])) >= 1
