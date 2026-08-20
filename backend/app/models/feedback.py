"""
backend/app/models/feedback.py
==============================
Phase 3.10 Analyst Feedback Loop Model.
Captures analyst triage verdicts (TRUE_POSITIVE, FALSE_POSITIVE, BENIGN, UNKNOWN)
and raw feature snapshots for model retraining datasets.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


VALID_FEEDBACK_VERDICTS = ["TRUE_POSITIVE", "FALSE_POSITIVE", "BENIGN", "UNKNOWN"]


class DetectionFeedback(Base):
    """
    Analyst feedback record capturing detection accuracy verdicts,
    analyst notes, and telemetry feature vectors for supervised model retraining.
    """
    __tablename__ = "detection_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    detection_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    flow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    predicted_attack_type: Mapped[str] = mapped_column(String(50), nullable=False)
    predicted_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    actual_verdict: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # TRUE_POSITIVE, FALSE_POSITIVE, BENIGN, UNKNOWN
    corrected_attack_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    analyst_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    analyst_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feature_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_used_for_retraining: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
