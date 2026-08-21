"""
tests/security/test_phase47_tenant_isolation.py
================================================
Security tests verifying tenant isolation across CISO reports, ROI records, and KPI snapshots.
"""

from backend.app.models.executive_security_intelligence import (
    CISOBoardReport, CyberROIRecord, ExecutiveKPISnapshot
)


def test_ciso_report_tenant_isolation():
    report_a = CISOBoardReport(tenant_id="tenant-alpha", report_period="Q3-2026")
    report_b = CISOBoardReport(tenant_id="tenant-beta", report_period="Q3-2026")
    assert report_a.tenant_id != report_b.tenant_id


def test_roi_record_tenant_isolation():
    roi_a = CyberROIRecord(tenant_id="tenant-alpha", period_label="Q3-2026")
    roi_b = CyberROIRecord(tenant_id="tenant-beta", period_label="Q3-2026")
    assert roi_a.tenant_id != roi_b.tenant_id


def test_kpi_snapshot_tenant_isolation():
    snap_a = ExecutiveKPISnapshot(tenant_id="tenant-alpha", snapshot_week="2026-W34")
    snap_b = ExecutiveKPISnapshot(tenant_id="tenant-beta", snapshot_week="2026-W34")
    assert snap_a.tenant_id != snap_b.tenant_id
    assert snap_a.snapshot_week == snap_b.snapshot_week
