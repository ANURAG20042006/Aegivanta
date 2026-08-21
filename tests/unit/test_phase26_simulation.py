"""
tests/unit/test_phase26_simulation.py
=====================================
Phase 26.2 Attack Simulation & Purple-Team Framework Unit Tests.
"""

import pytest
from backend.app.services.security_simulation_service import (
    SecuritySimulationService, ATTACK_TECHNIQUES_CATALOG
)


class TestSecuritySimulationService:
    """Unit tests for Purple-Team Attack Simulation Service."""

    def test_ten_techniques_catalog_populated(self):
        """All 10 required simulation techniques must be defined in the catalog."""
        assert len(ATTACK_TECHNIQUES_CATALOG) == 10

    def test_all_techniques_have_required_fields(self):
        """Each catalog technique must have name, tactic, technique_id, events, expected_detection, remediation."""
        for k, v in ATTACK_TECHNIQUES_CATALOG.items():
            assert "name" in v
            assert "tactic" in v
            assert "technique_id" in v
            assert len(v["events"]) > 0
            assert "expected_detection" in v
            assert "remediation" in v

    def test_all_simulation_events_tagged_as_simulation(self):
        """All synthetic events must have is_simulation=True flag for safety."""
        for k, v in ATTACK_TECHNIQUES_CATALOG.items():
            for ev in v["events"]:
                assert ev.get("is_simulation") is True

    def test_get_available_techniques_returns_ten_items(self):
        """get_available_techniques must return list of 10 items."""
        techniques = SecuritySimulationService.get_available_techniques()
        assert len(techniques) == 10
