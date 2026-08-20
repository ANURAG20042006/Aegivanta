"""
tests/unit/test_phase6_telemetry_schema.py
==========================================
Unit tests for Phase 6 Multi-Source Telemetry Schema Validation.
"""

import pytest
from backend.app.services.telemetry_ingestion_service import TelemetryIngestionService


def test_validate_network_flow_schema():
    """Validates complete 5-tuple network flow schema."""
    valid_flow = {
        "event_type": "NETWORK_FLOW",
        "data": {
            "src_ip": "10.0.0.1",
            "dst_ip": "1.1.1.1",
            "src_port": 44321,
            "dst_port": 443,
            "protocol": "TCP",
            "bytes": 2048,
            "packets": 12
        }
    }
    is_valid, reason = TelemetryIngestionService.validate_event(valid_flow)
    assert is_valid is True
    assert reason is None

    # Missing required field (dst_port)
    invalid_flow = {
        "event_type": "NETWORK_FLOW",
        "data": {
            "src_ip": "10.0.0.1",
            "dst_ip": "1.1.1.1",
            "src_port": 44321,
            "protocol": "TCP"
        }
    }
    is_valid_inv, reason_inv = TelemetryIngestionService.validate_event(invalid_flow)
    assert is_valid_inv is False
    assert "missing" in reason_inv.lower()


def test_validate_auth_and_dns_schemas():
    """Validates Auth event and DNS query schemas."""
    auth_ev = {
        "event_type": "AUTH_EVENT",
        "data": {
            "user": "sec_operator",
            "src_ip": "192.168.1.50",
            "success": True
        }
    }
    assert TelemetryIngestionService.validate_event(auth_ev)[0] is True

    dns_ev = {
        "event_type": "DNS_QUERY",
        "data": {
            "query_name": "malicious-c2.darknet",
            "query_type": "A"
        }
    }
    assert TelemetryIngestionService.validate_event(dns_ev)[0] is True
