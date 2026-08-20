import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.model_security_governance_service import ModelSecurityGovernanceService
from backend.app.models.ai_security_intelligence import AIModelGovernance


def test_hmac_signature_verification():
    raw_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    sig = ModelSecurityGovernanceService.generate_artifact_signature(raw_hash)
    assert len(sig) == 64

    assert ModelSecurityGovernanceService.verify_artifact_signature(raw_hash, sig) is True
    assert ModelSecurityGovernanceService.verify_artifact_signature(raw_hash, "tampered_signature_hex_code") is False


@pytest.mark.asyncio
async def test_model_lifecycle_promotion_and_rollback():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p20-gov"

        models = await ModelSecurityGovernanceService.list_models(db, tenant_id)
        assert len(models) >= 2

        canary_model = next((m for m in models if m["stage"] == "CANARY"), None)
        assert canary_model is not None

        # Promote to PRODUCTION
        promoted = await ModelSecurityGovernanceService.promote_model(
            db=db,
            tenant_id=tenant_id,
            model_id=canary_model["id"],
            target_stage="PRODUCTION"
        )
        assert promoted.stage == "PRODUCTION"
        assert promoted.is_active is True

        # Rollback
        rolled_back = await ModelSecurityGovernanceService.rollback_model(
            db=db,
            tenant_id=tenant_id,
            model_id=canary_model["id"]
        )
        assert rolled_back.stage == "ROLLED_BACK"
        assert rolled_back.is_active is False
