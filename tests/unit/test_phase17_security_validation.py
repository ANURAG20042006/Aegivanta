import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.security_validation_service import SecurityValidationService


@pytest.mark.asyncio
async def test_run_security_validation_suite():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-val"
        run = await SecurityValidationService.run_validation(db, tenant_id, "MANUAL")

        assert run is not None
        assert run.tenant_id == tenant_id
        assert run.total_checks >= 4
        assert run.passed_checks >= 3
        assert run.overall_score >= 70.0
        assert run.status in ["PASSED", "WARNING"]


@pytest.mark.asyncio
async def test_get_latest_validation_report():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-val-get"
        data = await SecurityValidationService.get_latest_validation(db, tenant_id)

        assert data is not None
        assert data["tenant_id"] == tenant_id
        assert len(data["checks"]) >= 4
        assert "MFA Policy Enforcement Verification" in [c["name"] for c in data["checks"]]
