from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.security_simulation_service import SecuritySimulationService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/security/simulations", tags=["Defensive Attack Simulations"])


class TriggerSimulationRequest(BaseModel):
    attack_technique: str


@router.post("", summary="Run Controlled Defensive Attack Simulation")
async def trigger_simulation(
    payload: TriggerSimulationRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes safe synthetic ATT&CK simulation and measures detection latency."""
    tenant_id = context.tenant_id or "default-tenant"
    sim = await SecuritySimulationService.run_simulation(
        db=db,
        tenant_id=tenant_id,
        technique_key=payload.attack_technique
    )
    return await SecuritySimulationService.get_simulation_details(db, sim.id, tenant_id)


@router.get("", summary="List Defensive Attack Simulations")
async def list_simulations(
    limit: int = Query(20, ge=1, le=50),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists historical simulation runs for the tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    sims = await SecuritySimulationService.list_simulations(db, tenant_id, limit)
    return [
        {
            "id": s.id,
            "simulation_name": s.simulation_name,
            "attack_technique": s.attack_technique,
            "tactic": s.tactic,
            "status": s.status,
            "coverage_result": s.coverage_result,
            "detection_latency_ms": s.detection_latency_ms,
            "created_at": s.created_at.isoformat()
        }
        for s in sims
    ]


@router.get("/{id}", summary="Get Attack Simulation Details")
async def get_simulation_details(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full simulation execution report with event latency breakdown."""
    tenant_id = context.tenant_id or "default-tenant"
    details = await SecuritySimulationService.get_simulation_details(db, id, tenant_id)
    if not details:
        raise SentinelAIException(status_code=404, detail="Simulation not found.")
    return details
