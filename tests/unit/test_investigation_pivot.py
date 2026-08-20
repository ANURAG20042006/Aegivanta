"""
tests/unit/test_investigation_pivot.py
======================================
Phase 3.8 Unit Tests: Multi-Dimensional Entity Pivoting Service.
"""

import pytest
from backend.app.services.investigation_pivot_service import InvestigationPivotService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_pivot_entity_structure():
    """Verify pivot structure returns typed buckets for correlated objects."""
    pivots = await InvestigationPivotService.pivot_entity(
        entity_type="IP",
        entity_value="198.51.100.99"
    )

    assert pivots["seed_entity_type"] == "IP"
    assert pivots["seed_entity_value"] == "198.51.100.99"
    assert "related_incidents" in pivots
    assert "related_alerts" in pivots
    assert "related_iocs" in pivots
    assert "related_actions" in pivots
