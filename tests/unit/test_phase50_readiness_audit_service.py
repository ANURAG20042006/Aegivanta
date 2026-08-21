"""
tests/unit/test_phase50_readiness_audit_service.py
==================================================
Unit tests for ProductionReadinessAuditService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.production_readiness_audit_service import ProductionReadinessAuditService
from backend.app.models.global_enterprise_certification import ProductionReadinessGate


@pytest.mark.asyncio
async def test_list_readiness_gates_with_mock():
    db = AsyncMock()
    mock_gate = ProductionReadinessGate(
        id="gate-1",
        tenant_id="tenant-gate-test",
        gate_name="Multi-Tenant Hard Isolation",
        gate_category="SECURITY",
        phase_origin="Phase 27",
        status="PASSED",
        benchmark_value="Zero Cross-Tenant Leakage",
        measured_value="Verified (100% Isolated)",
        is_critical_blocker=True
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_gate]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    gates = await ProductionReadinessAuditService.list_readiness_gates(
        db=db, tenant_id="tenant-gate-test"
    )
    assert isinstance(gates, list)
    assert len(gates) >= 1
    assert gates[0]["status"] == "PASSED"
    assert gates[0]["gate_name"] == "Multi-Tenant Hard Isolation"
