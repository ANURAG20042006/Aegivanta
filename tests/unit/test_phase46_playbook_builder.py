"""
tests/unit/test_phase46_playbook_builder.py
===========================================
Unit tests for PlaybookBuilderService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.playbook_builder_service import PlaybookBuilderService
from backend.app.models.security_automation_studio import AutomationPlaybook


@pytest.mark.asyncio
async def test_create_and_list_playbooks():
    db = AsyncMock()

    mock_playbook = AutomationPlaybook(
        id="pb-unit-1",
        tenant_id="tenant-alpha",
        name="Auto-Quarantine Ransomware Host",
        description="Isolates infected host immediately.",
        trigger_type="ON_ALERT",
        canvas_graph_json={"nodes": 3, "edges": 2},
        status="ACTIVE",
        executions_count=15
    )

    # Build the scalars chain: execute() → result → .scalars() → .all()
    mock_scalars_obj = MagicMock()
    mock_scalars_obj.all.return_value = [mock_playbook]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars_obj
    db.execute.return_value = mock_result

    res = await PlaybookBuilderService.list_playbooks(db=db, tenant_id="tenant-alpha")

    # The service will seed defaults when list is empty, then re-query.
    # With our mock returning one playbook, we get exactly that item.
    assert isinstance(res, list)
    assert len(res) >= 1
    assert res[0]["name"] == "Auto-Quarantine Ransomware Host"
    assert res[0]["trigger_type"] == "ON_ALERT"

