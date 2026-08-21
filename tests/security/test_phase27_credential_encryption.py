"""
tests/security/test_phase27_credential_encryption.py
====================================================
Phase 27 Credential Encryption & Secret Sanitization Security Tests.
"""

import pytest
from backend.app.services.cloud_account_connector_service import CloudAccountConnectorService


class TestCloudCredentialSecurity:
    """Security tests verifying that credentials cannot be accessed in plaintext."""

    def test_plaintext_secrets_never_stored_in_encrypted_string(self):
        """Encrypted token must never expose raw API keys or client secrets in plain text."""
        raw_creds = {
            "client_secret": "super_secret_azure_password_999!",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIE..."
        }
        encrypted = CloudAccountConnectorService.encrypt_credentials(raw_creds)
        assert "super_secret_azure_password_999!" not in encrypted
        assert "BEGIN RSA PRIVATE KEY" not in encrypted
