"""
backend/app/models/security_simulation.py
=========================================
Phase 17.5 Purple-Team Defensive Attack Simulation Framework Models.
Generates safe, non-destructive synthetic telemetry aligned with MITRE ATT&CK.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SecuritySimulation(Base):
    """Session record of synthetic defensive attack simulations."""
    __tablename__ = "security_simulations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    simulation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    attack_technique: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. T1110_BRUTE_FORCE, T1059_POWERSHELL, T1021_LATERAL_MOVEMENT
    tactic: Mapped[str] = mapped_column(String(100), nullable=False, default="Initial Access")

    status: Mapped[str] = mapped_column(String(30), default="COMPLETED", nullable=False) # RUNNING, COMPLETED, FAILED
    generated_events_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expected_detections_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    actual_detections_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    coverage_result: Mapped[str] = mapped_column(String(30), default="FULL", nullable=False) # FULL, PARTIAL, MISSED
    detection_latency_ms: Mapped[float] = mapped_column(Float, default=14.2, nullable=False)
    is_safe_simulation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SecuritySimulationEvent(Base):
    """Synthetic event injected through the detection pipeline during simulation."""
    __tablename__ = "security_simulation_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id: Mapped[str] = mapped_column(String(36), ForeignKey("security_simulations.id", ondelete="CASCADE"), nullable=False, index=True)

    event_seq: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    is_detected: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    matched_rule_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
