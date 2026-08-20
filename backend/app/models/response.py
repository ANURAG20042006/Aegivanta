"""
backend/app/models/response.py
==============================
Phase 3.7 SQLAlchemy Models for SOAR Autonomous Incident Response,
Centralized Policy Engine, Idempotency, and Audit Logs.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


VALID_ACTION_STATUSES = [
    "REQUESTED", "VALIDATING", "PENDING_APPROVAL", "APPROVED", "REJECTED",
    "EXECUTING", "VERIFYING", "SUCCEEDED", "FAILED",
    "ROLLBACK_REQUIRED", "ROLLING_BACK", "ROLLED_BACK", "BLOCKED"
]

ACTION_STATE_TRANSITIONS: Dict[str, List[str]] = {
    "REQUESTED": ["VALIDATING", "REJECTED", "BLOCKED"],
    "VALIDATING": ["PENDING_APPROVAL", "APPROVED", "BLOCKED", "FAILED"],
    "PENDING_APPROVAL": ["APPROVED", "REJECTED", "BLOCKED"],
    "APPROVED": ["EXECUTING", "BLOCKED"],
    "EXECUTING": ["VERIFYING", "FAILED", "ROLLBACK_REQUIRED"],
    "VERIFYING": ["SUCCEEDED", "FAILED", "ROLLBACK_REQUIRED"],
    "FAILED": ["ROLLBACK_REQUIRED", "BLOCKED"],
    "ROLLBACK_REQUIRED": ["ROLLING_BACK", "FAILED"],
    "ROLLING_BACK": ["ROLLED_BACK", "FAILED"],
    "SUCCEEDED": ["ROLLING_BACK", "ROLLBACK_REQUIRED"],
    "REJECTED": [],
    "ROLLED_BACK": [],
    "BLOCKED": []
}


def is_valid_action_transition(curr_status: str, next_status: str) -> bool:
    curr = curr_status.upper()
    nxt = next_status.upper()
    if curr == nxt:
        return True
    return nxt in ACTION_STATE_TRANSITIONS.get(curr, [])


class ResponsePolicy(Base):
    """Centralized, configurable automated incident response policy."""
    __tablename__ = "response_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    minimum_risk_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    minimum_severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    allowed_actions: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    max_actions_per_incident: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    allowed_target_types: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ResponseActionRecord(Base):
    """Execution record for an automated or analyst-initiated response action."""
    __tablename__ = "response_action_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ISOLATE_HOST, BLOCK_IP, QUARANTINE_ASSET, REVOKE_SESSION, DISABLE_ACCOUNT
    target_type: Mapped[str] = mapped_column(String(30), nullable=False, default="IP")  # IP, HOST, ASSET, USER
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    status: Mapped[str] = mapped_column(String(30), default="REQUESTED", nullable=False, index=True)
    is_dry_run: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    policy_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("response_policies.id", ondelete="SET NULL"), nullable=True)

    risk_score_at_execution: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    requested_by: Mapped[str] = mapped_column(String(100), nullable=False, default="SYSTEM")
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    execution_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    verification_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    rollback_status: Mapped[Optional[str]] = mapped_column(String(30), default="NONE", nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class IdempotencyRecord(Base):
    """Ensures deduplication and idempotent execution for response actions."""
    __tablename__ = "idempotency_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    action_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    incident_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    response_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ResponseAuditLog(Base):
    """Immutable audit trail for all SOAR policy evaluations and remediation actions."""
    __tablename__ = "response_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(30), nullable=False)
    action_name: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    result: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
