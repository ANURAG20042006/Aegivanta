"""
backend/app/models/ai_soc_ueba.py
=================================
Phase 37 AI SOC Autonomy, Insider Threat Defense & UEBA 2.0 Models.
Covers User & Entity Risk Scores (URS/ERS), Autonomous AI Investigation Cases,
Insider Threat Indicators, and Human-in-the-Loop Action Approval Decision Audits.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class UEBAUserProfile(Base):
    """
    User & Entity Behavior Analytics (UEBA 2.0) Baseline Profile.
    Tracks peer groups, behavioral anomaly deviations, and dynamic User Risk Score (URS).
    """
    __tablename__ = "ueba_user_profiles"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    user_email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(50), default="Engineering", nullable=False)
    peer_group: Mapped[str] = mapped_column(String(50), default="DevOps Engineers", nullable=False)

    user_risk_score: Mapped[int] = mapped_column(Integer, default=24, nullable=False)  # 0 to 100
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW

    baseline_login_hours: Mapped[str] = mapped_column(String(50), default="09:00 - 18:00 UTC", nullable=False)
    baseline_daily_egress_mb: Mapped[Float] = mapped_column(Float, default=450.0, nullable=False)
    anomalous_indicators_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_anomalies: Mapped[List[str]] = mapped_column(JSON, default=lambda: [], nullable=False)

    last_evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class AISOCInvestigation(Base):
    """
    Autonomous AI SOC Investigation Case.
    Captures autonomous alert triage, forensic evidence collection, and resolution plans.
    """
    __tablename__ = "ai_soc_investigations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    investigation_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    root_alert_id: Mapped[str] = mapped_column(String(100), default="ALT-88219", nullable=False)
    lead_hypothesis: Mapped[Text] = mapped_column(Text, nullable=False)

    investigation_state: Mapped[str] = mapped_column(String(50), default="TRIAGING", nullable=False)  # TRIAGING, EVIDENCE_COLLECTED, HUMAN_REVIEW_REQUIRED, RESOLVED_CLOSED
    triage_verdict: Mapped[str] = mapped_column(String(50), default="TRUE_POSITIVE_MALICIOUS", nullable=False)  # TRUE_POSITIVE_MALICIOUS, BENIGN_ANOMALY, POLICY_VIOLATION
    confidence_score: Mapped[Float] = mapped_column(Float, default=0.94, nullable=False)  # 0.00 to 1.00

    collected_evidence_items: Mapped[List[str]] = mapped_column(JSON, default=lambda: [], nullable=False)
    proposed_actions: Mapped[List[str]] = mapped_column(JSON, default=lambda: [], nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class InsiderThreatIndicator(Base):
    """
    Insider Threat & Data Hoarding Indicator.
    Flags unusual behavior patterns indicative of malicious or negligent insiders.
    """
    __tablename__ = "insider_threat_indicators"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    suspect_identity: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    anomaly_category: Mapped[str] = mapped_column(String(50), default="MASS_DOWNLOAD", nullable=False)  # MASS_DOWNLOAD, ODD_HOURS_ACCESS, PRIVILEGE_PROBING, CLOUD_HOARDING
    anomaly_magnitude_score: Mapped[int] = mapped_column(Integer, default=88, nullable=False)  # 0 to 100
    evidence_summary: Mapped[Text] = mapped_column(Text, nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class AISOCDecisionAudit(Base):
    """
    Human-in-the-Loop AI Decision Audit Ledger.
    Tracks every action proposed, approved, or auto-enforced by the AI SOC agent.
    """
    __tablename__ = "ai_soc_decision_audits"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    investigation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    proposed_action: Mapped[str] = mapped_column(String(255), nullable=False)
    impact_tier: Mapped[str] = mapped_column(String(30), default="CONTAINMENT", nullable=False)  # NON_DESTRUCTIVE, CONTAINMENT, HIGH_RISK

    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(30), default="APPROVED", nullable=False)  # APPROVED, REJECTED, PENDING_REVIEW, AUTO_ENFORCED
    decision_reasoning_trace: Mapped[Text] = mapped_column(Text, nullable=False)

    acted_by: Mapped[str] = mapped_column(String(100), default="lead_soc_analyst", nullable=False)
    audited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
