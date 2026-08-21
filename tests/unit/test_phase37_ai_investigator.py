"""
tests/unit/test_phase37_ai_investigator.py
==========================================
Phase 37 AI SOC Autonomous Investigator Unit Tests.
"""

import pytest
from backend.app.models.ai_soc_ueba import AISOCInvestigation


class TestAIInvestigator:
    """Unit tests for AISOCInvestigation model attributes."""

    def test_investigation_model_creation(self):
        """AISOCInvestigation must track title, root alert, hypothesis, verdict, and confidence."""
        inv = AISOCInvestigation(
            tenant_id="tenant-ai-soc",
            investigation_title="Anomalous Exfiltration",
            root_alert_id="ALT-1234",
            lead_hypothesis="Attacker compromised token",
            investigation_state="TRIAGING",
            triage_verdict="TRUE_POSITIVE_MALICIOUS",
            confidence_score=0.95,
            collected_evidence_items=["Evid 1"],
            proposed_actions=["Quarantine host"]
        )
        assert inv.investigation_title == "Anomalous Exfiltration"
        assert inv.confidence_score == 0.95
        assert inv.triage_verdict == "TRUE_POSITIVE_MALICIOUS"
