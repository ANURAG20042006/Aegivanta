"""
tests/unit/test_phase47_models.py
==================================
Unit tests for Phase 47 executive security intelligence models.
"""

from backend.app.models.executive_security_intelligence import (
    CISOBoardReport, CyberROIRecord, ExecutiveKPISnapshot
)


def test_ciso_board_report_model():
    r = CISOBoardReport(
        tenant_id="tenant-1",
        report_period="Q3-2026",
        report_type="QUARTERLY",
        overall_security_score=94.8,
        risk_posture_trend="IMPROVING",
        critical_findings_count=0,
        regulatory_compliance_score=97.2,
        mttr_days=0.08,
        incidents_prevented_count=1847,
        executive_summary="Board summary.",
        board_recommendations_json=["Rec1", "Rec2"],
        kpi_breakdown_json={"threats": 58492}
    )
    assert r.report_period == "Q3-2026"
    assert r.overall_security_score == 94.8
    assert r.risk_posture_trend == "IMPROVING"
    assert r.incidents_prevented_count == 1847


def test_cyber_roi_record_model():
    r = CyberROIRecord(
        tenant_id="tenant-1",
        period_label="Q3-2026",
        security_investment_usd=850000.0,
        estimated_losses_prevented_usd=12400000.0,
        roi_percentage=1359.0,
        breach_probability_reduction=0.87,
        cyber_insurance_savings_usd=145000.0,
        compliance_penalty_avoidance_usd=3200000.0,
        automation_labor_savings_usd=520000.0,
        top_roi_drivers_json=["Driver A"]
    )
    assert r.roi_percentage == 1359.0
    assert r.breach_probability_reduction == 0.87
    assert r.estimated_losses_prevented_usd == 12400000.0


def test_executive_kpi_snapshot_model():
    s = ExecutiveKPISnapshot(
        tenant_id="tenant-1",
        snapshot_week="2026-W34",
        threats_blocked_total=58492,
        critical_alerts_resolved=847,
        mean_detection_time_minutes=1.4,
        mean_response_time_minutes=4.8,
        sla_compliance_rate=0.9991,
        security_automation_coverage=0.84,
        top_attack_vectors_json=["Phishing", "Ransomware"],
        compliance_frameworks_status_json={"SOC2": "COMPLIANT"},
        trend_vs_prior_week_json={"mttr": "-2.0%"}
    )
    assert s.snapshot_week == "2026-W34"
    assert s.threats_blocked_total == 58492
    assert s.sla_compliance_rate == 0.9991
    assert s.security_automation_coverage == 0.84
