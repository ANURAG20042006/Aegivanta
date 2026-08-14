"""
tests/unit/test_phase3_attack_coverage.py
=========================================
Unit tests for MITRE ATT&CK Matrix Coverage Analytics.
"""

import pytest
from backend.app.database import AsyncSessionFactory
from backend.app.services.attack_coverage_service import AttackCoverageService


@pytest.mark.asyncio
async def test_attack_coverage_snapshot_computation():
    """Verify ATT&CK coverage calculation produces realistic percentages and tactic breakdowns."""
    async with AsyncSessionFactory() as db:
        snapshot = await AttackCoverageService.compute_coverage_snapshot(db)
        assert snapshot.id is not None
        assert snapshot.total_matrix_techniques > 0
        assert 0.0 <= snapshot.coverage_percentage <= 100.0
        assert "Reconnaissance" in snapshot.tactic_breakdown
        assert "Impact" in snapshot.tactic_breakdown
