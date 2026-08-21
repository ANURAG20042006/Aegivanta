"""
tests/unit/test_phase38_detection_engineering.py
================================================
Phase 38 Detection Engineering & Rule Compiler Unit Tests.
"""

import pytest
from backend.app.models.compliance_detection_eng import AutonomousDetectionRule


class TestDetectionEngineering:
    """Unit tests for AutonomousDetectionRule model."""

    def test_detection_rule_model_creation(self):
        """AutonomousDetectionRule must store rule name, syntax, MITRE technique, and lifecycle."""
        rule = AutonomousDetectionRule(
            tenant_id="tenant-comp",
            rule_name="Detect S3 Public ACL",
            rule_type="SIGMA_YAML",
            mitre_technique_id="T1530",
            rule_syntax_payload="title: S3 Public\ncondition: selection",
            lifecycle_state="CHAMPION",
            noise_score=5,
            true_positive_rate_pct=99.2
        )
        assert rule.rule_name == "Detect S3 Public ACL"
        assert rule.rule_type == "SIGMA_YAML"
        assert rule.lifecycle_state == "CHAMPION"
        assert rule.true_positive_rate_pct == 99.2
