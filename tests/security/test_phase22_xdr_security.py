"""
tests/security/test_phase22_xdr_security.py
============================================
Phase 22 Endpoint XDR & Zero-Trust Security Tests.
Validates response action constraints, tenant isolation, and governance controls.
"""

import pytest
from backend.app.services.endpoint_detection_service import EndpointDetectionService
from backend.app.services.zero_trust_engine import ZeroTrustEngine
from backend.app.models.endpoint_xdr import EndpointTelemetryEvent
from datetime import datetime, timezone


class TestXDRTenantIsolation:
    """Tests to verify tenant isolation in endpoint XDR services."""

    def _make_event(self, tenant_id: str, **kwargs):
        return EndpointTelemetryEvent(
            id="test-id",
            tenant_id=tenant_id,
            sensor_id="s1",
            hostname="WKS-01",
            event_category="PROCESS",
            process_name=kwargs.get("process_name", "notepad.exe"),
            process_cmdline=kwargs.get("process_cmdline", "notepad.exe"),
            parent_process_name=kwargs.get("parent_process_name"),
            severity="INFORMATIONAL",
            raw_event={},
            timestamp=datetime.now(timezone.utc)
        )

    def test_detection_analysis_is_stateless_per_event(self):
        """Detection engine produces no shared state between tenants."""
        event_t1 = self._make_event(
            "tenant-alpha",
            process_cmdline="vssadmin.exe delete shadows /all /quiet",
            parent_process_name="cmd.exe"
        )
        event_t2 = self._make_event(
            "tenant-beta",
            process_cmdline="notepad.exe",
            parent_process_name="explorer.exe"
        )
        dets_t1 = EndpointDetectionService.evaluate_telemetry_event(event_t1)
        dets_t2 = EndpointDetectionService.evaluate_telemetry_event(event_t2)

        # Ransomware only detected for t1
        t1_types = [d["detection_type"] for d in dets_t1]
        t2_types = [d["detection_type"] for d in dets_t2]
        assert "RANSOMWARE_BEHAVIOR" in t1_types
        assert "RANSOMWARE_BEHAVIOR" not in t2_types

    def test_zero_trust_score_is_pure_function_no_state_leakage(self):
        """Zero-trust scoring is pure and produces no shared state between callers."""
        score_a = ZeroTrustEngine.calculate_device_trust_score(
            "CRITICAL_PATCH_MISSING", "HEALTHY", "UNENCRYPTED", "DISABLED"
        )
        score_b = ZeroTrustEngine.calculate_device_trust_score(
            "UP_TO_DATE", "HEALTHY", "ENCRYPTED_BITLOCKER", "ENABLED"
        )
        # Subsequent calls must remain independent
        score_a2 = ZeroTrustEngine.calculate_device_trust_score(
            "CRITICAL_PATCH_MISSING", "HEALTHY", "UNENCRYPTED", "DISABLED"
        )
        assert score_a == score_a2
        assert score_b == 100.0
        assert score_a < score_b


class TestResponseActionGovernance:
    """Tests for endpoint response action validation."""

    def test_response_action_list_is_bounded(self):
        """Valid response action set is a controlled fixed list."""
        from backend.app.services.endpoint_response_service import VALID_RESPONSE_ACTIONS
        expected = {"ISOLATE_ENDPOINT", "TERMINATE_PROCESS", "REVOKE_SESSION", "RESET_CREDENTIALS", "RESTORE_ISOLATION"}
        assert set(VALID_RESPONSE_ACTIONS) == expected

    def test_response_action_rejects_invalid_types(self):
        """Invalid action types raise ValueError."""
        from backend.app.services.endpoint_response_service import EndpointResponseService
        import asyncio

        async def _run():
            from unittest.mock import AsyncMock, MagicMock
            db = MagicMock()
            db.flush = AsyncMock()
            db.add = MagicMock()
            with pytest.raises(ValueError, match="Unsupported endpoint response action"):
                await EndpointResponseService.execute_response_action(
                    db=db,
                    tenant_id="t1",
                    sensor_id="s1",
                    hostname="host",
                    action_type="DROP_DATABASE",  # Invalid
                    target_entity="host",
                    reason="test"
                )

        asyncio.run(_run())


class TestXDRCorrelationData:
    """Tests for XDR incident evidence graph structure."""

    def test_default_xdr_incident_has_required_fields(self):
        """Default XDR incidents have all required correlation fields."""
        from backend.app.services.xdr_correlation_engine import DEFAULT_XDR_INCIDENTS
        for inc in DEFAULT_XDR_INCIDENTS:
            assert "incident_title" in inc
            assert "severity" in inc
            assert "correlated_domains" in inc
            assert len(inc["correlated_domains"]) >= 3
            assert "evidence_graph" in inc
            assert "nodes" in inc["evidence_graph"]
            assert "edges" in inc["evidence_graph"]
            assert "root_cause_analysis" in inc
            assert len(inc["root_cause_analysis"]) > 20

    def test_xdr_incident_evidence_graph_nodes_have_type(self):
        """Evidence graph nodes each have a domain type."""
        from backend.app.services.xdr_correlation_engine import DEFAULT_XDR_INCIDENTS
        for inc in DEFAULT_XDR_INCIDENTS:
            for node in inc["evidence_graph"]["nodes"]:
                assert "type" in node
                assert node["type"] in ["ENDPOINT", "NETWORK", "IDENTITY", "CLOUD", "THREAT_INTEL"]
