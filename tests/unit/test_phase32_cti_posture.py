"""
tests/unit/test_phase32_cti_posture.py
======================================
Phase 32 CTI Posture & Hunting Query Generation Unit Tests.
"""

import pytest
from backend.app.services.cti_posture_service import CTIPostureService


class TestCTIPosture:
    """Unit tests for CTI posture scorecard and hunting query synthesizer."""

    def test_hunting_query_generation_synthesizes_kql_and_spl(self):
        """Threat hunting query generator must output valid KQL and SPL hunting strings."""
        queries = CTIPostureService.generate_hunting_queries("Volt Typhoon")
        assert len(queries) >= 2
        syntaxes = [q["syntax"] for q in queries]
        assert "KQL" in syntaxes
        assert "SPL" in syntaxes
        assert "T1059.001" in [q["technique_id"] for q in queries]
