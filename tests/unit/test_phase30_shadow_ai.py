"""
tests/unit/test_phase30_shadow_ai.py
====================================
Phase 30 Shadow AI Discovery Unit Tests.
"""

import pytest
from backend.app.models.llm_security import ShadowAIDiscoveryRecord


class TestShadowAI:
    """Unit tests for Shadow AI application discovery records."""

    def test_shadow_ai_model_initialization(self):
        """ShadowAIDiscoveryRecord model must store AI tool, user principal, and risk rating."""
        rec = ShadowAIDiscoveryRecord(
            tenant_id="tenant-123",
            ai_tool_name="ChatGPT (Consumer Web)",
            category="GENERATIVE_AI_CHATBOT",
            user_principal="john.doe@aegivanta.io",
            endpoint_hostname="WS-FINANCE-04",
            data_volume_mb=45.2,
            risk_rating="HIGH",
            is_corporate_approved=False,
            is_blocked=False
        )
        assert rec.ai_tool_name == "ChatGPT (Consumer Web)"
        assert rec.risk_rating == "HIGH"
        assert rec.is_corporate_approved is False
