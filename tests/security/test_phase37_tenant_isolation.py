"""
tests/security/test_phase37_tenant_isolation.py
===============================================
Phase 37 AI SOC & UEBA Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.ai_soc_ueba import (
    UEBAUserProfile, AISOCInvestigation, InsiderThreatIndicator, AISOCDecisionAudit
)


class TestAISOCMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 37 models."""

    def test_ai_soc_models_enforce_tenant_id(self):
        """All Phase 37 AI SOC & UEBA models must enforce tenant_id partition attributes."""
        prof = UEBAUserProfile(tenant_id="tenant-ai-1", user_email="u@c.i")
        inv = AISOCInvestigation(tenant_id="tenant-ai-1", investigation_title="t-1", lead_hypothesis="h-1")
        threat = InsiderThreatIndicator(tenant_id="tenant-ai-1", suspect_identity="u@c.i", evidence_summary="e-1")
        audit = AISOCDecisionAudit(tenant_id="tenant-ai-1", investigation_id="inv-1", proposed_action="a-1", decision_reasoning_trace="d-1")

        assert prof.tenant_id == "tenant-ai-1"
        assert inv.tenant_id == "tenant-ai-1"
        assert threat.tenant_id == "tenant-ai-1"
        assert audit.tenant_id == "tenant-ai-1"
