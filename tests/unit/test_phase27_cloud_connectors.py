"""
tests/unit/test_phase27_cloud_connectors.py
===========================================
Phase 27 Cloud Connector & Credential Encryption Unit Tests.
"""

import pytest
from backend.app.services.cloud_account_connector_service import CloudAccountConnectorService


class TestCloudAccountConnectors:
    """Unit tests for multi-cloud connector encryption and decryption."""

    def test_credential_encryption_roundtrip(self):
        """Fernet encryption and decryption must restore original JSON payload."""
        creds = {"role_arn": "arn:aws:iam::123456789012:role/Aegivanta", "external_id": "secret-ext-id-123"}
        encrypted = CloudAccountConnectorService.encrypt_credentials(creds)
        assert encrypted != str(creds)
        assert len(encrypted) > 40

        decrypted = CloudAccountConnectorService.decrypt_credentials(encrypted)
        assert decrypted == creds
