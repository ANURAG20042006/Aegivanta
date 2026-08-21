"""
tests/unit/test_phase38_models.py
=================================
Phase 38 Sandbox Execution Model Unit Tests.
"""

import pytest
from backend.app.models.compliance_detection_eng import DetectionSandboxExecution


class TestPhase38Models:
    """Unit tests for DetectionSandboxExecution model."""

    def test_sandbox_execution_model(self):
        """DetectionSandboxExecution must store rule ID, payload, match status, and latency."""
        exec_rec = DetectionSandboxExecution(
            tenant_id="tenant-comp",
            rule_id="rule-99",
            test_event_payload="powershell IEX DownloadString",
            match_status="MATCH_DETECTED",
            execution_time_ms=1.12,
            is_false_positive=False
        )
        assert exec_rec.rule_id == "rule-99"
        assert exec_rec.match_status == "MATCH_DETECTED"
        assert exec_rec.execution_time_ms == 1.12
