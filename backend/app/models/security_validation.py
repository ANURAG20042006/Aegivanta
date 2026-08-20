"""
backend/app/models/security_validation.py
=========================================
Phase 17.4 Continuous Security Defense Validation Models.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SecurityValidationRun(Base):
    """Execution session of the continuous defense verification framework."""
    __tablename__ = "security_validation_runs"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    trigger_type: Mapped[str] = mapped_column(String(50), default="SCHEDULED", nullable=False) # SCHEDULED, MANUAL, CI_CD
    status: Mapped[str] = mapped_column(String(30), default="RUNNING", nullable=False) # RUNNING, PASSED, WARNING, FAILED
    overall_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    total_checks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_checks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_checks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning_checks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SecurityValidationCheck(Base):
    """Individual security defense control test result within a validation run."""
    __tablename__ = "security_validation_checks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("security_validation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    check_category: Mapped[str] = mapped_column(String(50), nullable=False) # AUTH, TENANT_ISOLATION, SENSORS, DETECTION_RULES, SOAR_POLICY, AUDIT_INTEGRITY, COMPLIANCE
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="PASSED", nullable=False) # PASSED, WARNING, FAILED
    score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    execution_latency_ms: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)

    details_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
