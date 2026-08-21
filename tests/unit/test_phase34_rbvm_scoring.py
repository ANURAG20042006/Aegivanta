"""
tests/unit/test_phase34_rbvm_scoring.py
=======================================
Phase 34 RBVM Composite Risk Scoring Unit Tests.
"""

import pytest
from backend.app.services.rbvm_scoring_service import RBVMScoringService


class TestRBVMScoring:
    """Unit tests for composite RBVM risk calculation and SLA prioritization."""

    def test_critical_cve_with_high_epss_triggers_p0_24h_sla(self):
        """A CVE in CISA KEV with EPSS > 0.70 on a Tier 1 Asset must receive P0_CRITICAL and 24h SLA."""
        res = RBVMScoringService.calculate_rbvm_score(
            cvss_v3=9.8,
            epss_probability=0.92,
            in_cisa_kev=True,
            ransomware_associated=True,
            asset_tier="TIER_1_CRITICAL"
        )
        assert res["priority"] == "P0_CRITICAL"
        assert res["sla_hours"] == 24
        assert res["rbvm_score"] >= 90.0

    def test_low_epss_cve_receives_lower_priority(self):
        """A medium CVSS CVE with negligible EPSS probability must receive lower priority."""
        res = RBVMScoringService.calculate_rbvm_score(
            cvss_v3=5.5,
            epss_probability=0.01,
            in_cisa_kev=False,
            ransomware_associated=False,
            asset_tier="TIER_3_MEDIUM"
        )
        assert res["priority"] in ["P2_MEDIUM", "P3_LOW"]
        assert res["sla_hours"] >= 336
