"""
tests/unit/test_phase312_observability.py
==========================================
Phase 3.12 Unit Tests: Observability — metrics, structured logging, and secret redaction.
"""

import pytest
import json
import logging


class TestPrometheusMetrics:

    def test_metrics_module_imports_cleanly(self):
        """Metrics module must import without errors even if prometheus_client is absent."""
        import importlib
        import backend.app.observability.metrics as m
        assert hasattr(m, "api_requests_total")
        assert hasattr(m, "detections_total")
        assert hasattr(m, "ml_inference_total")
        assert hasattr(m, "incidents_created_total")
        assert hasattr(m, "ioc_matches_total")
        assert hasattr(m, "response_actions_total")
        assert hasattr(m, "redis_queue_depth")
        assert hasattr(m, "db_query_duration_seconds")
        assert hasattr(m, "audit_events_total")

    def test_record_api_request_does_not_raise(self):
        """record_api_request() must not raise even if prometheus_client is unavailable."""
        from backend.app.observability.metrics import record_api_request
        # Should be no-op or real, but never raise
        record_api_request("GET", "/api/v1/incidents", 200, 0.045)
        record_api_request("POST", "/api/v1/predict", 500, 1.2)
        record_api_request("GET", "/api/v1/alerts", 404, 0.001)

    def test_record_detection_does_not_raise(self):
        """record_detection() must not raise."""
        from backend.app.observability.metrics import record_detection
        record_detection("malicious", "DDoS", risk_score=87.5, duration_s=0.12)
        record_detection("benign", "BENIGN", risk_score=5.0, duration_s=0.03)

    def test_record_ml_inference_does_not_raise(self):
        """record_ml_inference() must not raise."""
        from backend.app.observability.metrics import record_ml_inference
        record_ml_inference("CatBoost", "malicious", 0.08, agreement_pct=80.0)
        record_ml_inference("LightGBM", "benign", 0.05)

    def test_record_incident_does_not_raise(self):
        """record_incident() must not raise."""
        from backend.app.observability.metrics import record_incident
        record_incident("create", "High")
        record_incident("resolve", "Critical", mttr_s=3600.0)

    def test_record_response_action_does_not_raise(self):
        """record_response_action() must not raise."""
        from backend.app.observability.metrics import record_response_action
        record_response_action("block_ip", "success")
        record_response_action("isolate_host", "failed")

    def test_get_metrics_response_returns_bytes_and_content_type(self):
        """get_metrics_response() must return (bytes, str) tuple."""
        from backend.app.observability.metrics import get_metrics_response
        content, content_type = get_metrics_response()
        assert isinstance(content, bytes)
        assert isinstance(content_type, str)
        assert len(content_type) > 0

    def test_null_metric_methods_are_callable(self):
        """_NullMetric must have callable inc/dec/set/observe/labels."""
        from backend.app.observability.metrics import _NullMetric
        nm = _NullMetric()
        nm.inc()
        nm.inc(5)
        nm.dec()
        nm.set(10)
        nm.observe(0.5)
        child = nm.labels(method="GET", endpoint="/test")
        child.inc()  # chained labels → inc


class TestStructuredLogging:

    def test_sanitize_strips_password_field(self):
        """sanitize_log_record must redact 'password' fields."""
        from backend.app.observability.structured_logging import sanitize_log_record
        record = {"username": "alice", "password": "super_secret_1234"}
        result = sanitize_log_record(record)
        assert result["password"] == "[REDACTED]"
        assert result["username"] == "alice"

    def test_sanitize_strips_api_key_field(self):
        """sanitize_log_record must redact 'api_key' fields."""
        from backend.app.observability.structured_logging import sanitize_log_record
        record = {"api_key": "sk-abc123xyz", "endpoint": "/v1/predict"}
        result = sanitize_log_record(record)
        assert result["api_key"] == "[REDACTED]"

    def test_sanitize_strips_jwt_value_by_pattern(self):
        """sanitize_log_record must redact JWT-shaped values even in non-sensitive keys."""
        from backend.app.observability.structured_logging import sanitize_log_record
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        record = {"note": f"Header: Bearer {jwt}"}
        result = sanitize_log_record(record)
        assert result["note"] == "[REDACTED]"

    def test_sanitize_strips_secret_field(self):
        """sanitize_log_record must redact 'secret' fields."""
        from backend.app.observability.structured_logging import sanitize_log_record
        result = sanitize_log_record({"secret": "my_db_password", "host": "db.example.com"})
        assert result["secret"] == "[REDACTED]"
        assert result["host"] == "db.example.com"

    def test_sanitize_recurses_into_nested_dicts(self):
        """sanitize_log_record must recursively redact in nested dicts."""
        from backend.app.observability.structured_logging import sanitize_log_record
        record = {
            "event": "login",
            "credentials": {
                "username": "bob",
                "password": "p@ssw0rd",
                "token": "ghp_abcdefghijklmnopqrstuvwxyz123456789"
            }
        }
        result = sanitize_log_record(record)
        assert result["credentials"]["password"] == "[REDACTED]"
        assert result["credentials"]["token"] == "[REDACTED]"
        assert result["credentials"]["username"] == "bob"

    def test_sanitize_preserves_non_sensitive_fields(self):
        """sanitize_log_record must not redact non-sensitive fields."""
        from backend.app.observability.structured_logging import sanitize_log_record
        record = {
            "event_type": "incident.created",
            "incident_id": "INC-001",
            "severity": "High",
            "risk_score": 87.5
        }
        result = sanitize_log_record(record)
        assert result == record

    def test_json_formatter_produces_valid_json(self):
        """StructuredJSONFormatter must produce parseable JSON for every log record."""
        from backend.app.observability.structured_logging import StructuredJSONFormatter
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="SentinelAI.test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test log message",
            args=(),
            exc_info=None
        )
        output = formatter.format(record)
        parsed = json.loads(output)  # must not raise

        assert "timestamp" in parsed
        assert "message" in parsed
        assert parsed["message"] == "Test log message"
        assert "severity" in parsed
        assert "service" in parsed

    def test_json_formatter_includes_required_fields(self):
        """Formatted log records must include all required structured fields."""
        from backend.app.observability.structured_logging import StructuredJSONFormatter
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="SentinelAI.detection",
            level=logging.WARNING,
            pathname="detection.py",
            lineno=42,
            msg="Anomaly detected",
            args=(),
            exc_info=None
        )
        parsed = json.loads(formatter.format(record))
        required_fields = ["timestamp", "service", "request_id", "trace_id", "event_type", "severity", "logger", "message"]
        for field in required_fields:
            assert field in parsed, f"Missing required field: '{field}'"

    def test_configure_structured_logging_is_idempotent(self):
        """configure_structured_logging called twice must not add duplicate handlers."""
        from backend.app.observability.structured_logging import configure_structured_logging, StructuredJSONFormatter
        root = logging.getLogger()
        initial_count = sum(1 for h in root.handlers if isinstance(h.formatter, StructuredJSONFormatter))
        configure_structured_logging()
        configure_structured_logging()
        final_count = sum(1 for h in root.handlers if isinstance(h.formatter, StructuredJSONFormatter))
        assert final_count == max(1, initial_count), "configure_structured_logging must be idempotent"

    def test_set_and_get_request_context(self):
        """set_request_context must persist request_id and trace_id via ContextVar."""
        from backend.app.observability.structured_logging import set_request_context, get_request_id, get_trace_id
        set_request_context(request_id="REQ-123", trace_id="TRC-456")
        assert get_request_id() == "REQ-123"
        assert get_trace_id() == "TRC-456"

    def test_set_request_context_auto_generates_request_id_if_empty(self):
        """set_request_context must auto-generate a UUID when request_id is not supplied."""
        from backend.app.observability.structured_logging import set_request_context, get_request_id
        set_request_context()
        rid = get_request_id()
        assert len(rid) > 0
        # Should look like a UUID (36 characters with 4 dashes)
        assert len(rid) == 36 or "-" in rid
