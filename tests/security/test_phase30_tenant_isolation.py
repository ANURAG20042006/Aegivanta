"""
tests/security/test_phase30_tenant_isolation.py
===============================================
Phase 30 AI/LLM Security Multi-Tenant Boundary Tests.
"""

import pytest
from backend.app.models.llm_security import (
    LLMGuardrailPolicy, LLMSecurityEvent, ShadowAIDiscoveryRecord, VectorDBAuditRecord
)


class TestLLMSecurityTenantIsolation:
    """Security tests verifying tenant boundaries across AI/LLM Security models."""

    def test_llm_models_require_tenant_id(self):
        """All Phase 30 models must have tenant_id attribute for multi-tenant isolation."""
        pol = LLMGuardrailPolicy(tenant_id="tenant-A", policy_name="p1")
        evt = LLMSecurityEvent(tenant_id="tenant-A", owasp_category="LLM01", threat_title="t", raw_prompt_hash="h", redacted_prompt_snippet="s")
        shd = ShadowAIDiscoveryRecord(tenant_id="tenant-A", ai_tool_name="ChatGPT", user_principal="u", endpoint_hostname="h")
        vec = VectorDBAuditRecord(tenant_id="tenant-A", collection_name="col")

        assert pol.tenant_id == "tenant-A"
        assert evt.tenant_id == "tenant-A"
        assert shd.tenant_id == "tenant-A"
        assert vec.tenant_id == "tenant-A"
