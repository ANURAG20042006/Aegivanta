import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base

VALID_JOB_STATUSES = ["QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "REJECTED", "PROMOTED"]


class TrainingJob(Base):
    """
    Persisted Training Job tracking asynchronous model retraining lifecycle state
    (QUEUED -> RUNNING -> SUCCEEDED / FAILED -> PROMOTED / REJECTED).
    """
    __tablename__ = "training_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED", nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(50), default="XGBoost Classifier", nullable=False)
    candidate_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    promotion_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
