"""
backend/app/models/security_insights.py
=======================================
Phase 16.8 & 16.9 Customer Security Value, Posture Improvement, and Cost Analytics Models.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SecurityScoreHistory(Base):
    """Tracks historical trajectory of organization and tenant security posture scores."""
    __tablename__ = "security_score_history"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    score: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_score: Mapped[int] = mapped_column(Integer, nullable=False)
    score_change: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


    category_scores: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class SecurityImprovementRecommendation(Base):
    """Explainable, prioritized security action recommendations with estimated impact points."""
    __tablename__ = "security_improvement_recommendations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False) # IDENTITY, SENSORS, POLICIES, ASSETS, THREAT_INTEL
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_impact_points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    action_type: Mapped[str] = mapped_column(String(50), nullable=False) # ENFORCE_MFA, ROTATE_SENSOR_TOKEN, UPDATE_POLICY, PATCH_ASSET
    action_target: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False) # PENDING, APPLIED, DISMISSED

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
