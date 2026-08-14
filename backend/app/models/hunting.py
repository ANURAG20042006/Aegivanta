"""
backend/app/models/hunting.py
=============================
SQLAlchemy Models for Advanced Threat Hunting Queries and Execution Logs.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class HuntingQuery(Base):
    """Stores saved parameterized threat hunting queries."""
    __tablename__ = "hunting_queries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    query_definition = Column(JSON, nullable=False)  # JSON structure: filters, time_range, entities
    created_by = Column(String(100), nullable=False)
    is_saved = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    executions = relationship("HuntingExecution", back_populates="query", cascade="all, delete-orphan")


class HuntingExecution(Base):
    """Audit log of threat hunting query executions and execution statistics."""
    __tablename__ = "hunting_executions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String, ForeignKey("hunting_queries.id", ondelete="SET NULL"), nullable=True, index=True)
    executed_by = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="COMPLETED", index=True)  # COMPLETED, FAILED, TIMEOUT
    result_count = Column(Integer, default=0)
    query_duration_ms = Column(Integer, default=0)
    parameters = Column(JSON, nullable=True)  # Captured query parameters

    query = relationship("HuntingQuery", back_populates="executions")
