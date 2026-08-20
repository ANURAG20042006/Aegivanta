import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.security_simulation_service import SecuritySimulationService
from backend.app.core.exceptions import SentinelAIException


@pytest.mark.asyncio
async def test_run_defensive_attack_simulation():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-sim-run"
        sim = await SecuritySimulationService.run_simulation(
            db=db,
            tenant_id=tenant_id,
            technique_key="T1110_BRUTE_FORCE"
        )

        assert sim is not None
        assert sim.tenant_id == tenant_id
        assert sim.status == "COMPLETED"
        assert sim.actual_detections_count >= 1
        assert sim.coverage_result == "FULL"
        assert sim.detection_latency_ms >= 0.0


@pytest.mark.asyncio
async def test_invalid_technique_raises_error():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-invalid-sim"
        with pytest.raises(SentinelAIException) as exc_info:
            await SecuritySimulationService.run_simulation(
                db=db,
                tenant_id=tenant_id,
                technique_key="INVALID_TECHNIQUE_XYZ"
            )
        assert exc_info.value.status_code == 400
