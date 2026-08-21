"""
backend/app/api/v1/sre_ops.py
=============================
Phase 26.12 & 26.13 Automated SRE, SLO, Error Budget & Chaos Engineering API Endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.sre_slo_validation_service import SRESLOValidationService
from backend.app.services.security_chaos_service import SecurityChaosService

router = APIRouter(prefix="/sre", tags=["Automated SRE, SLO & Security Chaos"])


class RunChaosRequest(BaseModel):
    scenario_key: str = Field(..., example="REDIS_OUTAGE")


@router.get("/health", summary="Get SRE Platform Infrastructure Health")
async def get_sre_health():
    """Returns real-time component health metrics, latencies, and system load."""
    return SRESLOValidationService.get_platform_sre_health()


@router.get("/slo", summary="Get 30-Day Rolling SLO Performance")
async def get_slo_performance():
    """Returns measured performance across all defined Service Level Objectives."""
    return SRESLOValidationService.get_slo_metrics()


@router.get("/error-budget", summary="Get Error Budget Consumption & Burn Rate")
async def get_error_budget():
    """Calculates error budget burn rate and projected breach forecasting."""
    return SRESLOValidationService.get_error_budget_analytics()


@router.get("/chaos/scenarios", summary="List Security Chaos Scenarios")
async def list_chaos_scenarios():
    """Lists supported non-destructive failure injection test scenarios."""
    return SecurityChaosService.list_scenarios()


@router.post("/chaos/run", summary="Run Security Chaos Simulation")
async def run_chaos_simulation(
    req: RunChaosRequest,
    context: TenantContext = Depends(resolve_tenant_context)
):
    """Executes a non-destructive fault injection simulation and verifies fallback resilience."""
    tenant_id = context.tenant_id or "default-tenant"
    return SecurityChaosService.run_chaos_simulation(
        scenario_key=req.scenario_key,
        tenant_id=tenant_id
    )
