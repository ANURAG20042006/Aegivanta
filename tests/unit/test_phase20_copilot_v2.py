import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.ai_copilot_v2_service import AICopilotV2Service


@pytest.mark.asyncio
async def test_ai_copilot_reasoning_and_remediation_gating():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p20-copilot"
        user_id = "ANALYST_SEC"

        prompt = "Investigate suspicious data exfiltration from 10.0.0.45 to 198.51.100.22"
        res = await AICopilotV2Service.chat_reason(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            prompt=prompt
        )

        assert res["session_id"] is not None
        assert res["is_prompt_injection_flagged"] is False
        assert len(res["contributing_signals"]) > 0
        assert len(res["hunting_queries"]) > 0
        assert len(res["remediation_proposals"]) > 0
        assert res["requires_human_approval"] is True
        assert all(p["requires_approval"] is True for p in res["remediation_proposals"])
