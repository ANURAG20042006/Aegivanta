"""
tests/unit/test_phase28_identity_governance.py
==============================================
Phase 28 Identity Governance & Posture Unit Tests.
"""

import pytest
from backend.app.models.identity import IdentityScorecard, PasskeyCredential


class TestIdentityGovernance:
    """Unit tests for identity scorecards and passkey models."""

    def test_passkey_model_initialization(self):
        """PasskeyCredential model must initialize with hardware binding fields."""
        key = PasskeyCredential(
            tenant_id="tenant-123",
            user_id="usr-789",
            credential_id="cred_yubikey_001",
            public_key_pem="-----BEGIN PUBLIC KEY-----\n...",
            device_nickname="YubiKey 5C NFC",
            sign_count=5,
            is_backup_eligible=True
        )
        assert key.credential_id == "cred_yubikey_001"
        assert key.device_nickname == "YubiKey 5C NFC"
        assert key.sign_count == 5

    def test_identity_scorecard_dormancy(self):
        """IdentityScorecard flags dormancy correctly."""
        card = IdentityScorecard(
            tenant_id="tenant-123",
            user_id="usr-789",
            username="dormant.user@aegivanta.io",
            identity_risk_score=75.0,
            risk_tier="HIGH",
            is_dormant=True,
            last_login_days_ago=120,
            mfa_enabled=False
        )
        assert card.is_dormant is True
        assert card.last_login_days_ago == 120
