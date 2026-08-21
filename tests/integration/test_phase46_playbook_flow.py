"""
tests/integration/test_phase46_playbook_flow.py
===============================================
Integration tests for Playbook creation and lifecycle management.
"""

import pytest
from unittest.mock import AsyncMock
from backend.app.services.playbook_builder_service import PlaybookBuilderService


@pytest.mark.asyncio
async def test_playbook_lifecycle_flow():
    db = AsyncMock()
    created = await PlaybookBuilderService.create_playbook(
        db=db,
        tenant_id="tenant-prod",
        name="Integration Playbook Test",
        description="End-to-end DAG execution test.",
        trigger_type="ON_ALERT"
    )

    assert created["name"] == "Integration Playbook Test"
    assert created["status"] == "ACTIVE"
    assert "canvas_graph_json" in created
    assert len(created["canvas_graph_json"]["nodes"]) == 3
