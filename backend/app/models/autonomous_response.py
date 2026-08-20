"""
backend/app/models/autonomous_response.py
=========================================
Phase 17.1, 17.2, 17.11 & 17.12 Autonomous Response Orchestration, Autonomy Levels,
Blast-Radius Guards, and Automated Rollback Models.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class AutonomousResponsePolicy(Base):
    """Tenant-controlled autonomous response policy with configurable autonomy levels."""
    __tablename__ = "autonomous_response_policies"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Autonomy Levels: LEVEL_0_OBSERVE, LEVEL_1_RECOMMEND, LEVEL_2_APPROVAL_REQUIRED, LEVEL_3_LIMITED_AUTONOMOUS, LEVEL_4_FULL_AUTONOMOUS
    autonomy_level: Mapped[str] = mapped_column(String(50), default="LEVEL_2_APPROVAL_REQUIRED", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    min_confidence_threshold: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    min_risk_threshold: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    max_blast_radius_assets: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    allowed_actions: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    excluded_assets: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)

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


class ResponsePolicyRule(Base):
    """Atomic rule criteria evaluated during autonomous response decision making."""
    __tablename__ = "response_policy_rules"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("autonomous_response_policies.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    condition_type: Mapped[str] = mapped_column(String(50), nullable=False) # ATTACK_TYPE, RISK_SCORE, SEVERITY, ASSET_CRITICALITY
    operator: Mapped[str] = mapped_column(String(20), default="EQ", nullable=False) # EQ, GTE, LTE, CONTAINS
    target_value: Mapped[str] = mapped_column(String(255), nullable=False)

    action_type: Mapped[str] = mapped_column(String(50), nullable=False) # ISOLATE_ENDPOINT, BLOCK_IP, BLOCK_IOC, DISABLE_API_KEY, REVOKE_SESSION
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ResponseBlastRadius(Base):
    """Calculated blast-radius guard record predicting downstream impact of containment actions."""
    __tablename__ = "response_blast_radii"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    affected_assets_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    affected_users_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    affected_sensors_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    contains_production_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_business_impact: Mapped[str] = mapped_column(String(20), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    rollback_supported: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ResponseRollback(Base):
    """Reversible action transaction log for safe automated and manual rollback."""
    __tablename__ = "response_rollbacks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False)

    original_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    modified_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    rollback_operation: Mapped[str] = mapped_column(String(100), nullable=False)

    rollback_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False) # PENDING, COMPLETED, FAILED
    executed_by: Mapped[str] = mapped_column(String(100), default="SYSTEM", nullable=False)

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
