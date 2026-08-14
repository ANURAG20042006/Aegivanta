"""
backend/app/models/response_approval.py
=======================================
SQLAlchemy Models for Controlled SOAR Remediation Requests and Approvals.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, ForeignKey
from backend.app.database import Base


class ResponseApproval(Base):
    """Tracks two-tier response action approval workflows and authorization decisions."""
    __tablename__ = "response_approvals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_action = Column(String(100), nullable=False, index=True)  # NOTIFY_ANALYST, CREATE_TICKET, ESCALATE_INCIDENT, BLOCK_IOC_SIMULATION, ISOLATE_ASSET_SIMULATION, DISABLE_ACCOUNT_SIMULATION
    target_entity = Column(String(255), nullable=False)
    parameters = Column(JSON, nullable=True)
    
    requested_by = Column(String(100), nullable=False)
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    rejected_by = Column(String(100), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    status = Column(String(50), default="REQUESTED", index=True)  # REQUESTED, APPROVED, REJECTED, EXECUTING, COMPLETED, FAILED, CANCELLED
    reason = Column(Text, nullable=True)
    is_dry_run = Column(Boolean, default=True, nullable=False)  # Enforce simulation by default
    
    execution_id = Column(String(255), nullable=True)  # ID of the resulting execution
    execution_result = Column(JSON, nullable=True)
    audit_id = Column(String(255), nullable=True, index=True)
