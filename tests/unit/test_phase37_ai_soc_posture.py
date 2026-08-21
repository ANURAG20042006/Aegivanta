"""
tests/unit/test_phase37_ai_soc_posture.py
=========================================
Phase 37 AI SOC Decision Audit Unit Tests.
"""

import pytest
from backend.app.models.ai_soc_ueba import AISOCDecisionAudit


class TestAISOCPosture:
    """Unit tests for AISOCDecisionAudit model."""

    def test_decision_audit_model(self):
        """AISOCDecisionAudit must track proposed action, impact tier, approval status, and reason."""
        audit = AISOCDecisionAudit(
            tenant_id="tenant-ai-soc",
            investigation_id="inv-1234",
            proposed_action="Quarantine Endpoint",
            impact_tier="CONTAINMENT",
            requires_human_approval=True,
            approval_status="APPROVED",
            decision_reasoning_trace="True positive malicious activity verified.",
            acted_by="commander_01"
        )
        assert audit.proposed_action == "Quarantine Endpoint"
        assert audit.approval_status == "APPROVED"
        assert audit.requires_human_approval is True
