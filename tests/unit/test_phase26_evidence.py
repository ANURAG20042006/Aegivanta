"""
tests/unit/test_phase26_evidence.py
===================================
Phase 26.7 Forensic Evidence & Chain of Custody Unit Tests.
"""

import pytest
from backend.app.services.evidence_custody_service import EvidenceCustodyService
from backend.app.models.evidence_custody import EVIDENCE_TYPES, CUSTODY_ACTIONS


class TestEvidenceCustody:
    """Unit tests for evidence cryptographic hashing and sanitization."""

    def test_evidence_types_defined(self):
        """All 10 required evidence types must exist."""
        assert len(EVIDENCE_TYPES) == 10

    def test_custody_actions_defined(self):
        """All required chain-of-custody actions must exist."""
        required = {"COLLECTED", "TRANSFERRED", "ANALYZED", "VERIFIED", "EXPORTED", "SEALED", "ARCHIVED"}
        assert required.issubset(set(CUSTODY_ACTIONS))

    def test_compute_payload_hash_deterministic(self):
        """Hashing the same payload multiple times must produce the identical SHA-256 hex digest."""
        payload = {"event_id": "123", "command": "powershell.exe -enc AA=="}
        h1 = EvidenceCustodyService.compute_payload_hash(payload)
        h2 = EvidenceCustodyService.compute_payload_hash(payload)
        assert h1 == h2
        assert len(h1) == 64

    def test_compute_payload_hash_order_independent(self):
        """Keys in different order must yield identical canonical hash."""
        p1 = {"a": 1, "b": 2}
        p2 = {"b": 2, "a": 1}
        assert EvidenceCustodyService.compute_payload_hash(p1) == EvidenceCustodyService.compute_payload_hash(p2)

    def test_sanitize_evidence_payload_redacts_tokens(self):
        """Secrets in evidence payload must be redacted."""
        raw = {"cmd": "curl -H 'Authorization: Bearer ak_12345678901234567890123456789012' https://example.com"}
        clean = EvidenceCustodyService.sanitize_evidence_payload(raw)
        assert "[REDACTED_API_KEY]" in clean["cmd"]
