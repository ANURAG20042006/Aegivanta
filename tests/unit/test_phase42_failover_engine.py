"""
tests/unit/test_phase42_failover_engine.py
==========================================
Phase 42 Failover Execution Event Unit Tests.
"""

import pytest
from backend.app.models.multi_region_resilience import FailoverExecutionEvent


class TestFailoverEngine:
    """Unit tests for FailoverExecutionEvent model."""

    def test_failover_event_model_creation(self):
        """FailoverExecutionEvent must store source, target, trigger, and duration."""
        evt = FailoverExecutionEvent(
            tenant_id="tenant-multi",
            source_failing_region="US_EAST_PRIMARY",
            target_failover_region="EU_WEST_SECONDARY",
            failover_trigger="OPERATOR_INITIATED",
            switchover_duration_ms=380.0,
            status="SUCCESS"
        )
        assert evt.source_failing_region == "US_EAST_PRIMARY"
        assert evt.target_failover_region == "EU_WEST_SECONDARY"
        assert evt.status == "SUCCESS"
        assert evt.switchover_duration_ms == 380.0
