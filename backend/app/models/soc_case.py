"""
backend/app/models/soc_case.py
==============================
Phase 26 Enterprise SOC Case Management Models.
Supports full case lifecycle: OPEN -> TRIAGED -> INVESTIGATING -> CONTAINMENT ->
REMEDIATION -> MONITORING -> RESOLVED -> CLOSED -> REOPENED.
Includes SLA tracking, tasks, watchers, comments, and immutable audit logging.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

SOC_CASE_STATUSES = [
    "OPEN", "TRIAGED", "INVESTIGATING", "CONTAINMENT",
    "REMEDIATION", "MONITORING", "RESOLVED", "CLOSED", "REOPENED"
]

SOC_CASE_PRIORITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


class SOCCase(Base):
    """Primary Enterprise SOC Case management model with SLA and post-incident review."""
    __tablename__ = "soc_cases"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    case_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)

    lead_analyst_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    assigned_team: Mapped[str] = mapped_column(String(100), default="SOC Tier 2", nullable=False)

    linked_incident_ids: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    linked_alert_ids: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    affected_assets: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    affected_identities: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    mitre_attack_techniques: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    sla_target_hours: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_sla_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, default=75.0, nullable=False)
    containment_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False) # PENDING, IN_PROGRESS, CONTAINED, FAILED
    post_incident_review: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_by: Mapped[str] = mapped_column(String(100), default="SYSTEM", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    tasks = relationship("SOCCaseTask", back_populates="case", cascade="all, delete-orphan")
    comments = relationship("SOCCaseComment", back_populates="case", cascade="all, delete-orphan")
    audits = relationship("SOCCaseAudit", back_populates="case", cascade="all, delete-orphan")


class SOCCaseTask(Base):
    """Investigation and containment subtask assigned to analysts."""
    __tablename__ = "soc_case_tasks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("soc_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    case = relationship("SOCCase", back_populates="tasks")


class SOCCaseComment(Base):
    """Analyst investigation notes and collaboration stream."""
    __tablename__ = "soc_case_comments"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("soc_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    author: Mapped[str] = mapped_column(String(100), nullable=False)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    case = relationship("SOCCase", back_populates="comments")


class SOCCaseAudit(Base):
    """Immutable audit trail of all state modifications on an investigation case."""
    __tablename__ = "soc_case_audits"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("soc_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    action: Mapped[str] = mapped_column(String(100), nullable=False) # STATUS_CHANGED, ANALYST_ASSIGNED, TASK_ADDED, EVIDENCE_LINKED, SLA_ESCALATED
    performed_by: Mapped[str] = mapped_column(String(100), nullable=False)
    old_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    case = relationship("SOCCase", back_populates="audits")
