"""
backend/app/models/threat_hunting_v2.py
=======================================
Phase 26 Threat Hunting Workbench V2 Models.
Supports saved searches, complex investigation query templates, execution tracking,
and linking hunting discoveries directly to SOC Cases.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SavedHuntingQuery(Base):
    """Reusable threat hunting query template with bounded complexity and entity filters."""
    __tablename__ = "saved_hunting_queries"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_string: Mapped[str] = mapped_column(Text, nullable=False)
    target_data_source: Mapped[str] = mapped_column(String(50), default="TELEMETRY", nullable=False) # TELEMETRY, ENDPOINT, NETWORK, AUTH, DNS, THREAT_INTEL

    mitre_attack_techniques: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class HuntingInvestigationSession(Base):
    """Execution session of a Threat Hunting hypothesis with linked matches and case references."""
    __tablename__ = "hunting_investigation_sessions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    query_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("saved_hunting_queries.id", ondelete="SET NULL"), nullable=True)

    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    matched_events_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    findings_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    linked_case_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("soc_cases.id", ondelete="SET NULL"), nullable=True)
    is_threat_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    analyst: Mapped[str] = mapped_column(String(100), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
