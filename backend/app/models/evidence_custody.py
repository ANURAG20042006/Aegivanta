"""
backend/app/models/evidence_custody.py
======================================
Phase 26 Forensic Evidence & Chain of Custody Models.
Stores cryptographically verified evidence artifacts (SHA-256) and logs
immutable chain of custody transition events.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base

EVIDENCE_TYPES = [
    "NETWORK_EVENT", "ENDPOINT_EVENT", "PROCESS_EVENT", "AUTHENTICATION_EVENT",
    "ALERT", "SCREENSHOT_METADATA", "LOG_REFERENCE", "THREAT_INTEL_INDICATOR",
    "ANALYST_NOTE", "DETECTION_RESULT"
]

CUSTODY_ACTIONS = [
    "COLLECTED", "TRANSFERRED", "ANALYZED", "VERIFIED", "EXPORTED", "SEALED", "ARCHIVED"
]


class ForensicEvidenceItem(Base):
    """Immutable forensic evidence item with cryptographic SHA-256 fingerprint."""
    __tablename__ = "forensic_evidence_items"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("soc_cases.id", ondelete="SET NULL"), nullable=True, index=True)

    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. aegivanta.edr, aegivanta.sensor, zeek, suricata

    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True) # SHA-256 hash of payload
    raw_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False) # Sanitized evidence data

    integrity_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    collected_by: Mapped[str] = mapped_column(String(100), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    custody_events = relationship("EvidenceCustodyEvent", back_populates="evidence_item", cascade="all, delete-orphan")


class EvidenceCustodyEvent(Base):
    """Immutable audit entry in the forensic chain of custody ledger."""
    __tablename__ = "evidence_custody_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evidence_id: Mapped[str] = mapped_column(String(36), ForeignKey("forensic_evidence_items.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    action: Mapped[str] = mapped_column(String(50), nullable=False) # COLLECTED, TRANSFERRED, ANALYZED, VERIFIED, SEALED
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    source_custodian: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_custodian: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    verification_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    is_tamper_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    evidence_item = relationship("ForensicEvidenceItem", back_populates="custody_events")
