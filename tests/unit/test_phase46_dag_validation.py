"""
tests/unit/test_phase46_dag_validation.py
=========================================
Unit tests for DAG graph validation and template listings.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.playbook_builder_service import PlaybookBuilderService
from backend.app.models.security_automation_studio import PlaybookTemplate


@pytest.mark.asyncio
async def test_list_templates():
    db = AsyncMock()
    mock_template = PlaybookTemplate(
        id="tpl-1",
        tenant_id="tenant-alpha",
        name="AWS GuardDuty Crypto-Mining Quarantine",
        category="CLOUD_SECURITY",
        description="Quarantines compromised EC2 instance.",
        default_graph_json={"steps": 4},
        verified=True
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_template]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    templates = await PlaybookBuilderService.list_templates(db=db, tenant_id="tenant-alpha")
    assert len(templates) >= 1
    assert templates[0]["category"] == "CLOUD_SECURITY"
    assert templates[0]["verified"] is True
