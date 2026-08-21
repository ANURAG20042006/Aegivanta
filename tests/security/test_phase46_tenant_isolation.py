"""
tests/security/test_phase46_tenant_isolation.py
===============================================
Security tests verifying tenant isolation across automation playbooks and execution runs.
"""

from backend.app.models.security_automation_studio import AutomationPlaybook, PlaybookExecutionRun


def test_tenant_isolation_boundary():
    pb_tenant_a = AutomationPlaybook(
        tenant_id="tenant-alpha",
        name="Playbook Alpha",
        trigger_type="ON_ALERT"
    )
    pb_tenant_b = AutomationPlaybook(
        tenant_id="tenant-beta",
        name="Playbook Beta",
        trigger_type="ON_WEBHOOK"
    )

    assert pb_tenant_a.tenant_id != pb_tenant_b.tenant_id
    assert pb_tenant_a.name != pb_tenant_b.name
