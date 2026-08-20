"""
backend/app/models/alert_intelligence.py
========================================
Phase 16.2 & 16.3 Alert Intelligence, Deduplication, and Prioritization Models.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class AlertFingerprint(Base):
    """Tracks unique signatures of alert patterns for deduplication and temporal aggregation."""
    __tablename__ = "alert_fingerprints"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fingerprint_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    source_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    attack_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    signature: Mapped[str] = mapped_column(String(255), nullable=False)

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_suppressed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AlertGroup(Base):
    """Correlated cluster of alerts grouped under a parent incident with entity context."""
    __tablename__ = "alert_groups"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_code: Mapped[str] = mapped_column(String(50), default=lambda: f"GRP-{uuid.uuid4().hex[:8].upper()}", unique=True, nullable=False)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    root_attack_type: Mapped[str] = mapped_column(String(50), nullable=False)
    alert_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)

    affected_assets: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    source_ips: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    mitre_techniques: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class AlertPriorityScore(Base):
    """Explainable risk-based prioritization score (0–100) with contributing factor breakdown."""
    __tablename__ = "alert_priority_scores"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=50.0) # 0.0 to 100.0
    priority_level: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL

    contributing_factors: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    reasons: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
