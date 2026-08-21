"""
tests/unit/test_phase37_insider_threat.py
=========================================
Phase 37 Insider Threat Detector Unit Tests.
"""

import pytest
from backend.app.models.ai_soc_ueba import InsiderThreatIndicator


class TestInsiderThreat:
    """Unit tests for InsiderThreatIndicator model."""

    def test_insider_threat_model(self):
        """InsiderThreatIndicator must track suspect identity, category, magnitude, and evidence."""
        threat = InsiderThreatIndicator(
            tenant_id="tenant-ai-soc",
            suspect_identity="disgruntled@corp.internal",
            anomaly_category="MASS_DOWNLOAD",
            anomaly_magnitude_score=94,
            evidence_summary="Downloaded 500 confidential files"
        )
        assert threat.suspect_identity == "disgruntled@corp.internal"
        assert threat.anomaly_category == "MASS_DOWNLOAD"
        assert threat.anomaly_magnitude_score == 94
