"""
tests/security/test_phase29_secret_scanning.py
==============================================
Phase 29 Secret Scanning & Credential Exposure Security Tests.
"""

import pytest
from backend.app.services.cicd_gatekeeper_service import CICDGatekeeperService


class TestSecretScanningSecurity:
    """Security tests validating high-entropy secret scanner regexes and entropy filters."""

    def test_aws_and_github_token_detection(self):
        """Scanner must detect AWS Access Key and GitHub PAT in text."""
        code_sample = '''
        def configure_aws():
            aws_key = "AKIAIOSFODNN7EXAMPLE"
            gh_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
            return True
        '''
        res = CICDGatekeeperService.scan_content_for_secrets(code_sample)
        assert res["is_clean"] is False
        assert res["secrets_detected_count"] >= 2
        types = [f["secret_type"] for f in res["findings"]]
        assert "AWS_ACCESS_KEY" in types
        assert "GITHUB_PAT" in types

    def test_clean_code_passes_secret_scanner(self):
        """Code without secrets must return is_clean = True."""
        clean_sample = '''
        def add(a, b):
            return a + b
        '''
        res = CICDGatekeeperService.scan_content_for_secrets(clean_sample)
        assert res["is_clean"] is True
        assert res["secrets_detected_count"] == 0
