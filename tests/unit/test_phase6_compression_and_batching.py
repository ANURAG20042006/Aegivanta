"""
tests/unit/test_phase6_compression_and_batching.py
==================================================
Unit tests for Gzip/Zlib Decompression and Batch Payload Expansion Controls.
"""

import gzip
import json
import pytest
from backend.app.services.telemetry_ingestion_service import TelemetryIngestionService
from backend.app.core.exceptions import SentinelAIException


def test_gzip_decompression_and_json_parsing():
    """Validates transparent decompression of gzip telemetry bytes."""
    payload = {
        "schema_version": "v1",
        "events": [
            {"event_type": "DNS_QUERY", "data": {"query_name": "example.com", "query_type": "A"}}
        ]
    }
    raw_json = json.dumps(payload).encode("utf-8")
    compressed = gzip.compress(raw_json)

    result = TelemetryIngestionService.decompress_payload(compressed, content_encoding="gzip")
    assert result["schema_version"] == "v1"
    assert len(result["events"]) == 1


def test_payload_size_limit_rejection():
    """Oversized payloads (>10MB) must be rejected with 413 Payload Too Large."""
    oversized_data = b"X" * (11 * 1024 * 1024)
    with pytest.raises(SentinelAIException) as exc_info:
        TelemetryIngestionService.decompress_payload(oversized_data)
    assert exc_info.value.status_code == 413
