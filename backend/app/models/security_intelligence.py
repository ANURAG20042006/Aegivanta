"""
backend/app/models/security_intelligence.py
===========================================
Phase 17.6, 17.8 & 17.9 Detection Coverage Gaps, Asset Risk Scores & Control Effectiveness Models.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class DetectionCoverageGap(Base):
    """Identified ATT&CK coverage deficit or weak rule detection posture."""
    __tablename__ = "detection_coverage_gaps"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    technique_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g. T1059.001
    technique_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tactic: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. Execution, Defense Evasion

    risk_level: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    current_coverage_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    missing_controls: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    recommended_detection: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_telemetry: Mapped[str] = mapped_column(Text, nullable=False)

    priority_rank: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False) # OPEN, MITIGATED, ACCEPTED

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class AssetRiskScore(Base):
    """Dynamic multi-factor 0–100 risk score and attack-path vulnerability index per protected asset."""
    __tablename__ = "asset_risk_scores"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("protected_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    risk_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False) # 0.0 to 100.0
    risk_level: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL

    contributing_factors: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SecurityControlEffectiveness(Base):
    """Empirical measurement of active defensive controls mitigating real threats."""
    __tablename__ = "security_control_effectiveness"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    control_name: Mapped[str] = mapped_column(String(100), nullable=False) # MFA, SSO, DETECTION_ENGINE, SENSORS, SOAR, THREAT_INTEL
    effectiveness_score: Mapped[float] = mapped_column(Float, default=95.0, nullable=False) # 0.0 to 100.0

    blocked_threats_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    missed_threats_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failures_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    response_latency_ms: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.95, nullable=False)
    recommended_improvement: Mapped[str] = mapped_column(Text, nullable=False)

    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
