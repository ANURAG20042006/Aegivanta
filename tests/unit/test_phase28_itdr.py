"""
tests/unit/test_phase28_itdr.py
===============================
Phase 28 Identity Threat Detection & Response (ITDR) Unit Tests.
"""

import pytest
from backend.app.models.identity import IdentityThreatDetection


class TestITDRThreats:
    """Unit tests for ITDR threat models and MITRE ATT&CK mapping."""

    def test_itdr_model_initialization(self):
        """IdentityThreatDetection model must initialize with threat type and MITRE technique."""
        det = IdentityThreatDetection(
            tenant_id="tenant-123",
            threat_type="MFA_FATIGUE",
            target_username="john.doe@aegivanta.io",
            source_ip="198.51.100.42",
            geo_location="Frankfurt, Germany",
            severity="HIGH",
            risk_score=85.0,
            mitre_attack_id="T1621",
            is_blocked=True,
            action_taken="STEP_UP_MFA_ENFORCED"
        )
        assert det.threat_type == "MFA_FATIGUE"
        assert det.mitre_attack_id == "T1621"
        assert det.is_blocked is True
