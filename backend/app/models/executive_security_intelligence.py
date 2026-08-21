"""
backend/app/models/executive_security_intelligence.py
======================================================
Phase 47 — Executive Security Intelligence, Cyber ROI & CISO Posture Reporting.

Models:
- CISOBoardReport     : Board-level CISO posture report snapshot (quarterly / on-demand)
- CyberROIRecord      : Quantified financial cyber risk metrics per reporting period
- ExecutiveKPISnapshot: Executive dashboard KPI snapshot (weekly cadence)
"""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    DateTime, JSON
)
from backend.app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CISOBoardReport(Base):
    """Quarterly CISO board-level posture report."""
    __tablename__ = "ciso_board_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")

    report_period = Column(String(50), nullable=False, default="Q3-2026")   # e.g. Q3-2026
    report_type = Column(String(50), nullable=False, default="QUARTERLY")   # QUARTERLY, ON_DEMAND
    overall_security_score = Column(Float, nullable=False, default=94.8)
    risk_posture_trend = Column(String(20), nullable=False, default="IMPROVING")  # IMPROVING, STABLE, DECLINING
    critical_findings_count = Column(Integer, nullable=False, default=0)
    regulatory_compliance_score = Column(Float, nullable=False, default=97.2)
    mttr_days = Column(Float, nullable=False, default=0.08)   # Mean Time To Remediate in days
    incidents_prevented_count = Column(Integer, nullable=False, default=1847)
    executive_summary = Column(Text, nullable=False, default="")
    board_recommendations_json = Column(JSON, nullable=False, default=list)
    kpi_breakdown_json = Column(JSON, nullable=False, default=dict)
    generated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<CISOBoardReport {self.report_period} score={self.overall_security_score}>"


class CyberROIRecord(Base):
    """Quantified cyber ROI and financial risk metrics per reporting period."""
    __tablename__ = "cyber_roi_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")

    period_label = Column(String(50), nullable=False, default="Q3-2026")
    security_investment_usd = Column(Float, nullable=False, default=850000.0)
    estimated_losses_prevented_usd = Column(Float, nullable=False, default=12400000.0)
    roi_percentage = Column(Float, nullable=False, default=1359.0)
    breach_probability_reduction = Column(Float, nullable=False, default=0.87)    # 87% reduction
    cyber_insurance_savings_usd = Column(Float, nullable=False, default=145000.0)
    compliance_penalty_avoidance_usd = Column(Float, nullable=False, default=3200000.0)
    automation_labor_savings_usd = Column(Float, nullable=False, default=520000.0)
    top_roi_drivers_json = Column(JSON, nullable=False, default=list)
    calculated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<CyberROIRecord {self.period_label} roi={self.roi_percentage}%>"


class ExecutiveKPISnapshot(Base):
    """Weekly executive dashboard KPI snapshot."""
    __tablename__ = "executive_kpi_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")

    snapshot_week = Column(String(20), nullable=False, default="2026-W34")
    threats_blocked_total = Column(Integer, nullable=False, default=58492)
    critical_alerts_resolved = Column(Integer, nullable=False, default=847)
    mean_detection_time_minutes = Column(Float, nullable=False, default=1.4)
    mean_response_time_minutes = Column(Float, nullable=False, default=4.8)
    sla_compliance_rate = Column(Float, nullable=False, default=0.9991)
    security_automation_coverage = Column(Float, nullable=False, default=0.84)
    top_attack_vectors_json = Column(JSON, nullable=False, default=list)
    compliance_frameworks_status_json = Column(JSON, nullable=False, default=dict)
    trend_vs_prior_week_json = Column(JSON, nullable=False, default=dict)
    captured_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<ExecutiveKPISnapshot {self.snapshot_week}>"
