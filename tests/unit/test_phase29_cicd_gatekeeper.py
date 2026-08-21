"""
tests/unit/test_phase29_cicd_gatekeeper.py
==========================================
Phase 29 CI/CD Gatekeeper Policy Unit Tests.
"""

import pytest
from backend.app.models.supply_chain import PipelineSecurityGate


class TestCICDGatekeeper:
    """Unit tests for pipeline deployment gatekeeper policies."""

    def test_pipeline_gate_model_initialization(self):
        """PipelineSecurityGate model must initialize with blocking mode and CVE thresholds."""
        gate = PipelineSecurityGate(
            tenant_id="tenant-123",
            gate_name="Production Gate",
            target_environment="PRODUCTION",
            enforcement_mode="BLOCKING",
            max_critical_cves=0,
            max_high_cves=2,
            require_slsa_level_3=True,
            disallow_copyleft_licenses=True,
            require_secret_scan_clean=True,
            is_active=True
        )
        assert gate.target_environment == "PRODUCTION"
        assert gate.enforcement_mode == "BLOCKING"
        assert gate.max_critical_cves == 0
