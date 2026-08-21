"""
tests/unit/test_phase46_models.py
=================================
Unit tests for Phase 46 Security Automation Studio models.
"""

from backend.app.models.security_automation_studio import (
    AutomationPlaybook, PlaybookExecutionRun, PlaybookTemplate
)


def test_models_instantiation():
    pb = AutomationPlaybook(
        tenant_id="tenant-1",
        name="Test Playbook",
        description="Testing DAG",
        trigger_type="ON_SCHEDULE",
        canvas_graph_json={"nodes": [], "edges": []},
        status="ACTIVE"
    )
    assert pb.name == "Test Playbook"
    assert pb.status == "ACTIVE"

    run = PlaybookExecutionRun(
        tenant_id="tenant-1",
        playbook_id="pb-1",
        playbook_name="Test Playbook",
        trigger_event="CRON_15M",
        current_step="COMPLETED",
        duration_ms=85.0,
        status="COMPLETED"
    )
    assert run.duration_ms == 85.0
    assert run.status == "COMPLETED"

    tpl = PlaybookTemplate(
        tenant_id="tenant-1",
        name="Template Alpha",
        category="INCIDENT_RESPONSE",
        description="Demo",
        verified=True
    )
    assert tpl.verified is True

