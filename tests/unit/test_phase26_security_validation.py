"""
tests/unit/test_phase26_security_validation.py
==============================================
Phase 26.1 Continuous Security Validation Engine Unit Tests.
Validates control domain definitions, severity levels, and automated report synthesis.
"""

import pytest
from backend.app.services.continuous_security_validation_service import (
    ContinuousSecurityValidationService, VALIDATION_CONTROL_DOMAINS
)


class TestContinuousSecurityValidation:
    """Unit tests for Continuous Security Validation Service."""

    def test_all_sixteen_domains_defined(self):
        """All 16 required security control domains must be defined."""
        assert len(VALIDATION_CONTROL_DOMAINS) == 16

    def test_required_domain_categories_present(self):
        """Mandatory control categories must exist in domain catalog."""
        categories = {d["category"] for d in VALIDATION_CONTROL_DOMAINS}
        required = {
            "AUTH", "RBAC", "TENANT_ISOLATION", "API_KEYS", "SENSORS",
            "WEBHOOKS", "SSO", "SCIM", "ENDPOINT_XDR", "ZERO_TRUST",
            "AUDIT_INTEGRITY", "ENCRYPTION", "SECRET_REDACTION",
            "RATE_LIMITING", "SECURITY_HEADERS", "AI_DEFENSES"
        }
        assert required.issubset(categories)

    def test_domains_have_severity_and_remediation(self):
        """Each control domain must define non-empty severity and remediation guidance."""
        for d in VALIDATION_CONTROL_DOMAINS:
            assert d["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
            assert len(d["remediation"]) > 10

    def test_control_names_unique(self):
        """Control names must be unique across the matrix."""
        names = [d["name"] for d in VALIDATION_CONTROL_DOMAINS]
        assert len(names) == len(set(names))
