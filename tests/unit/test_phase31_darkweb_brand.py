"""
tests/unit/test_phase31_darkweb_brand.py
========================================
Phase 31 Dark Web Credential Leaks & Brand Protection Unit Tests.
"""

import pytest
from backend.app.models.attack_surface import DarkWebCredentialLeak, BrandImpersonationAlert


class TestDarkWebBrand:
    """Unit tests for Dark Web breaches and brand impersonation alerts."""

    def test_darkweb_credential_leak_model(self):
        """DarkWebCredentialLeak must store employee email, breach source, and plaintext flag."""
        leak = DarkWebCredentialLeak(
            tenant_id="tenant-123",
            employee_email="sarah.connor@aegivanta.io",
            breach_source="RedLine Stealer Botnet Dump",
            password_hash_sample="85f6a81b...",
            is_plaintext_exposed=True,
            severity="CRITICAL",
            is_remediated=False
        )
        assert leak.employee_email == "sarah.connor@aegivanta.io"
        assert leak.severity == "CRITICAL"
        assert leak.is_plaintext_exposed is True

    def test_brand_impersonation_model(self):
        """BrandImpersonationAlert must store typosquatted domain, similarity score, and MX status."""
        alert = BrandImpersonationAlert(
            tenant_id="tenant-123",
            impersonating_domain="aeglvanta.io",
            levenshtein_similarity_score=0.94,
            registrar_name="NameCheap, Inc.",
            has_active_mx_records=True,
            has_live_web_server=True,
            threat_status="ACTIVE_PHISHING_LURE"
        )
        assert alert.impersonating_domain == "aeglvanta.io"
        assert alert.levenshtein_similarity_score == 0.94
        assert alert.has_active_mx_records is True
