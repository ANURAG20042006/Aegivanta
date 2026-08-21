"""
tests/unit/test_phase30_ai_posture.py
=====================================
Phase 30 AI Security Posture & Guardrail Policies Unit Tests.
"""

import pytest
from backend.app.models.llm_security import LLMGuardrailPolicy


class TestAIPosture:
    """Unit tests for guardrail policies and security configurations."""

    def test_guardrail_policy_model_initialization(self):
        """LLMGuardrailPolicy must initialize with blocking mode and threshold limits."""
        policy = LLMGuardrailPolicy(
            tenant_id="tenant-123",
            policy_name="Global Enterprise LLM Guardrail",
            target_model_endpoint="ALL_LLM_ENDPOINTS",
            enforcement_mode="BLOCKING",
            block_prompt_injection=True,
            prompt_injection_threshold=0.75,
            redact_pii=True,
            block_system_prompt_leakage=True,
            sanitize_output_xss=True,
            max_tokens_per_prompt=4096,
            is_active=True
        )
        assert policy.enforcement_mode == "BLOCKING"
        assert policy.block_prompt_injection is True
        assert policy.max_tokens_per_prompt == 4096
