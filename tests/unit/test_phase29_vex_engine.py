"""
tests/unit/test_phase29_vex_engine.py
=====================================
Phase 29 OpenVEX Exploitability Engine Unit Tests.
"""

import pytest
from backend.app.models.supply_chain import VEXStatement


class TestVEXEngine:
    """Unit tests for OpenVEX statement lifecycle and justifications."""

    def test_vex_statement_model_initialization(self):
        """VEXStatement must record vulnerability ID and non-exploitability justification."""
        stmt = VEXStatement(
            tenant_id="tenant-123",
            vulnerability_id="CVE-2026-10492",
            product_purl="pkg:npm/jsonwebtoken@9.0.2",
            status="NOT_AFFECTED",
            justification="Vulnerable code is not invoked by execution path",
            impact_statement="Only RS256 algorithm active."
        )
        assert stmt.vulnerability_id == "CVE-2026-10492"
        assert stmt.status == "NOT_AFFECTED"
