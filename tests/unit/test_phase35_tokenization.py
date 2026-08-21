"""
tests/unit/test_phase35_tokenization.py
=======================================
Phase 35 Cryptographic Tokenization Vault Unit Tests.
"""

import pytest
from backend.app.models.dlp_security import TokenizedDataVault


class TestTokenizationVault:
    """Unit tests for TokenizedDataVault model attributes."""

    def test_token_vault_model_creation(self):
        """TokenizedDataVault must store token identifier, surrogate value, and cipher algorithm."""
        token = TokenizedDataVault(
            tenant_id="tenant-dlp",
            token_identifier="TKN-PCI-001",
            surrogate_token_value="TKN-4111-XXXX-XXXX-9912",
            token_format="FPE_CREDIT_CARD",
            cipher_algorithm="AES_256_GCM",
            encrypted_blob_payload="ENC:v1:gcm:testblob",
            authorized_roles=["admin", "compliance_officer"]
        )
        assert token.token_identifier == "TKN-PCI-001"
        assert token.token_format == "FPE_CREDIT_CARD"
        assert "compliance_officer" in token.authorized_roles
