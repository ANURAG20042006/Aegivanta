"""
backend/app/models/job.py
=========================
SQLAlchemy Models for Resilient Background Jobs, Failure Isolation & Audit.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Integer, JSON, DateTime
from backend.app.database import Base


class BackgroundJob(Base):
    """Tracks background job lifecycles, retry attempts, and failure records."""
    __tablename__ = "background_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(100), nullable=False, index=True)  # THREAT_FEED_SYNC, MONITORING_POLL, FORECAST_COMPUTATION, ATTACK_MATRIX_SYNC
    status = Column(String(50), default="PENDING", index=True)  # PENDING, RUNNING, COMPLETED, FAILED, RETRYING
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
