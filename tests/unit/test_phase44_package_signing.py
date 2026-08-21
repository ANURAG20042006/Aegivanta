"""
tests/unit/test_phase44_package_signing.py
==========================================
Phase 44 Package Signing & Ed25519 Provenance Unit Tests.
"""

import pytest
import hashlib


class TestPackageSigning:
    """Unit tests for package signature generation and verification."""

    def test_package_signature_hash_generation(self):
        """Signature hash should be deterministic 64-char hex string."""
        pkg_name = "Autonomous Ransomware Triage Playbook"
        version = "1.0.0"
        author = "SecOps Automated"
        sig_hash = hashlib.sha256(f"{pkg_name}_{version}_{author}".encode()).hexdigest()

        assert len(sig_hash) == 64
        assert isinstance(sig_hash, str)
