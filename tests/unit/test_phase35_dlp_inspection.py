"""
tests/unit/test_phase35_dlp_inspection.py
=========================================
Phase 35 DLP Luhn Algorithm & Payload Inspection Unit Tests.
"""

import pytest
from backend.app.services.dlp_inspection_service import DLPInspectionService


class TestDLPInspection:
    """Unit tests for Luhn checksum algorithm and payload inspection."""

    def test_luhn_algorithm_validation(self):
        """Valid Luhn credit cards must return True; invalid cards must return False."""
        # Standard valid test card PANs (e.g. Visa test card 4111 1111 1111 1111)
        valid_pan = "4111111111111111"
        invalid_pan = "4111111111111112"

        assert DLPInspectionService.validate_luhn_credit_card(valid_pan) is True
        assert DLPInspectionService.validate_luhn_credit_card(invalid_pan) is False

    def test_inspect_payload_detects_ssn_and_aws_key(self):
        """Payload containing SSN and AWS Access Key must be classified and masked."""
        raw_text = "Employee John Doe SSN 987-65-4321 with AWS Key AKIAIOSFODNN7EXAMPLE"
        res = DLPInspectionService.inspect_text_payload(raw_text)

        assert res["is_violating"] is True
        assert res["findings_count"] >= 2
        assert "XXX-XX-4321" in res["sanitized_payload"]
        assert "AKIA****************" in res["sanitized_payload"]
