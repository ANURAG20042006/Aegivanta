"""
backend/app/models/compliance_detection_eng.py
=============================================
Phase 38 Autonomous Detection Engineering & Multi-Standard Compliance Models.
Covers Autonomous Detection Rules (Sigma/YARA-L), Sandbox Executions,
Multi-Standard Compliance Controls (SOC 2, ISO 27001, HIPAA, FedRAMP, PCI-DSS 4.0),
and Auditor Attestation Reports.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class AutonomousDetectionRule(Base):
    """
    Autonomous Detection-as-Code Candidate Rule.
    Tracks Sigma / YARA-L rules, noise scores, and champion/challenger states.
    """
    __tablename__ = "autonomous_detection_rules"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    rule_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(50), default="SIGMA_YAML", nullable=False)  # SIGMA_YAML, YARA_L, BEHAVIORAL_PYTHON
    mitre_technique_id: Mapped[str] = mapped_column(String(50), default="T1059.001", nullable=False)
    rule_syntax_payload: Mapped[Text] = mapped_column(Text, nullable=False)

    lifecycle_state: Mapped[str] = mapped_column(String(50), default="CHAMPION", nullable=False)  # SANDBOX_TESTED, CHAMPION, CHALLENGER, DEPRECATED
    noise_score: Mapped[int] = mapped_column(Integer, default=12, nullable=False)  # 0 to 100
    true_positive_rate_pct: Mapped[Float] = mapped_column(Float, default=98.5, nullable=False)
    evaluated_telemetry_count: Mapped[int] = mapped_column(Integer, default=145000, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ComplianceFrameworkControl(Base):
    """
    Multi-Standard Compliance Control Assessment.
    Supports SOC 2 Type II, ISO/IEC 27001:2022, HIPAA, FedRAMP High, and PCI-DSS 4.0.
    """
    __tablename__ = "compliance_framework_controls"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    framework: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # SOC2_TYPE2, ISO_27001, HIPAA, FEDRAMP_HIGH, PCI_DSS_4
    control_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # CC6.1, A.9.2.1, 164.312(a)(1), AC-2, Req-3.4
    control_title: Mapped[str] = mapped_column(String(255), nullable=False)

    compliance_status: Mapped[str] = mapped_column(String(50), default="PASS_COMPLIANT", nullable=False)  # PASS_COMPLIANT, FAIL_NON_COMPLIANT, DRIFT_DETECTED
    automated_evidence_summary: Mapped[Text] = mapped_column(Text, nullable=False)
    drift_details: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    last_assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ComplianceAuditReport(Base):
    """
    Exportable Compliance Audit Attestation Report.
    """
    __tablename__ = "compliance_audit_reports"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    framework: Mapped[str] = mapped_column(String(50), nullable=False)
    overall_compliance_score: Mapped[Float] = mapped_column(Float, default=97.8, nullable=False)
    passing_controls_count: Mapped[int] = mapped_column(Integer, default=64, nullable=False)
    failing_controls_count: Mapped[int] = mapped_column(Integer, default=2, nullable=False)

    auditor_attestation_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_by: Mapped[str] = mapped_column(String(100), default="compliance_officer", nullable=False)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DetectionSandboxExecution(Base):
    """
    Detection Rule Sandbox Test Execution Record.
    """
    __tablename__ = "detection_sandbox_executions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    rule_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    test_event_payload: Mapped[Text] = mapped_column(Text, nullable=False)
    match_status: Mapped[str] = mapped_column(String(50), default="MATCH_DETECTED", nullable=False)  # MATCH_DETECTED, NO_MATCH
    execution_time_ms: Mapped[Float] = mapped_column(Float, default=1.45, nullable=False)
    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
