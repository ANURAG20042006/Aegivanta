"""
backend/app/models/investigation.py
===================================
Phase 3.8 Investigation Case Management, Evidence Aggregation,
Investigation Notes, and Chronological Case Timelines.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


VALID_CASE_STATUSES = [
    "OPEN", "TRIAGED", "INVESTIGATING", "ESCALATED", "CONTAINED", "RESOLVED", "CLOSED"
]

CASE_STATE_TRANSITIONS: Dict[str, List[str]] = {
    "OPEN": ["TRIAGED", "INVESTIGATING", "CLOSED"],
    "TRIAGED": ["INVESTIGATING", "ESCALATED", "CLOSED"],
    "INVESTIGATING": ["ESCALATED", "CONTAINED", "RESOLVED", "CLOSED"],
    "ESCALATED": ["INVESTIGATING", "CONTAINED", "RESOLVED", "CLOSED"],
    "CONTAINED": ["RESOLVED", "INVESTIGATING", "CLOSED"],
    "RESOLVED": ["CLOSED", "INVESTIGATING"],
    "CLOSED": ["OPEN", "INVESTIGATING"]
}


def is_valid_case_transition(curr_status: str, next_status: str) -> bool:
    curr = curr_status.upper()
    nxt = next_status.upper()
    if curr == nxt:
        return True
    return nxt in CASE_STATE_TRANSITIONS.get(curr, [])


class InvestigationCase(Base):
    """Primary investigation case container correlating incidents, assets, users, and evidence."""
    __tablename__ = "investigation_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    priority: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False, index=True)
    analyst: Mapped[str] = mapped_column(String(100), default="unassigned", nullable=False, index=True)

    linked_incident_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    linked_assets: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    linked_users: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    linked_iocs: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    mitre_techniques: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    risk_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)

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
    notes = relationship("InvestigationNote", back_populates="case", cascade="all, delete-orphan")
    evidence_items = relationship("InvestigationEvidence", back_populates="case", cascade="all, delete-orphan")
    timeline_events = relationship("InvestigationTimeline", back_populates="case", cascade="all, delete-orphan")


class InvestigationNote(Base):
    """Analyst investigation notes and forensic hypothesis tracking."""
    __tablename__ = "investigation_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    case = relationship("InvestigationCase", back_populates="notes")


class InvestigationTimeline(Base):
    """Chronological investigation case timeline events."""
    __tablename__ = "investigation_timelines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # TELEMETRY, DETECTION, ALERT, IOC, PIVOT, REMEDIATION, NOTE
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    actor: Mapped[str] = mapped_column(String(100), default="SYSTEM", nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    case = relationship("InvestigationCase", back_populates="timeline_events")


class Investigation(Base):
    """Legacy incident-level automated analysis record (preserved for backward compatibility)."""
    __tablename__ = "investigations"

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    asset_id = mapped_column(String(36), ForeignKey("protected_assets.id", ondelete="SET NULL"), nullable=True, index=True)

    status = mapped_column(String(30), default="COMPLETED", index=True)
    summary = mapped_column(Text, nullable=False)
    findings = mapped_column(JSON, default=dict)
    attack_chain_stage = mapped_column(String(50), default="RECONNAISSANCE", index=True)
    confidence_score = mapped_column(Float, default=0.90)
    recommended_actions = mapped_column(JSON, default=list)

    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incident = relationship("Incident", backref="investigation")
    asset = relationship("ProtectedAsset")
    evidence = relationship("InvestigationEvidence", back_populates="investigation", cascade="all, delete-orphan")


class InvestigationEvidence(Base):
    """Traceable empirical evidence item associated with an investigation case or incident."""
    __tablename__ = "investigation_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True, index=True)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=True, index=True)

    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    investigation = relationship("Investigation", back_populates="evidence")
    case = relationship("InvestigationCase", back_populates="evidence_items")
