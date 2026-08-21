"""
tests/unit/test_phase27_serverless.py
=====================================
Phase 27 Serverless Security Posture Unit Tests.
"""

import pytest
from backend.app.models.cloud_security import ServerlessFunctionRisk


class TestServerlessSecurity:
    """Unit tests for Serverless Function risk auditing."""

    def test_serverless_risk_model_fields(self):
        """ServerlessFunctionRisk model must track public URLs and wildcard IAM flags."""
        risk = ServerlessFunctionRisk(
            tenant_id="tenant-123",
            provider="AWS",
            function_arn="arn:aws:lambda:us-east-1:123456789012:function:demo",
            function_name="demo",
            runtime="python3.11",
            has_public_url=True,
            has_unencrypted_env_vars=True,
            has_wildcard_iam=True,
            vulnerable_dependencies_count=1,
            risk_score=85.0,
            remediation_advice="Encrypt environment variables."
        )
        assert risk.has_public_url is True
        assert risk.has_wildcard_iam is True
        assert risk.risk_score == 85.0
