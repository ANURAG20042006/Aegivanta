"""
backend/app/models/soar_v2.py
=============================
Phase 19 Autonomous SOC & SOAR 2.0 Models:
Declarative Playbooks, Playbook Versions, Step-Level Executions,
SOAR Connectors, Connector Health, and Emergency Kill Switch.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class DeclarativePlaybook(Base):
    """Declarative SOAR Playbook definition with triggers, action sequence, and versioning."""
    __tablename__ = "declarative_playbooks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="CONTAINMENT", nullable=False) # CONTAINMENT, INVESTIGATION, ENRICHMENT, REMEDIATION
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PUBLISHED", nullable=False) # DRAFT, PUBLISHED, ARCHIVED

    trigger_type: Mapped[str] = mapped_column(String(50), default="ALERT_CRITICAL", nullable=False) # ALERT_CRITICAL, INCIDENT_HIGH, IOC_SIGHTING, MANUAL
    trigger_conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)

    # Step Sequence: list of {step_id, action_type, target_entity, timeout_sec, retry_count, requires_approval, on_failure}
    steps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    retry_policy: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)

    created_by: Mapped[str] = mapped_column(String(100), default="ADMIN", nullable=False)
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


class SOARExecutionSession(Base):
    """Execution session tracking the end-to-end execution of a SOAR playbook."""
    __tablename__ = "soar_execution_sessions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    playbook_id: Mapped[str] = mapped_column(String(36), ForeignKey("declarative_playbooks.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    alert_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    is_dry_run: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True) # PENDING, AWAITING_APPROVAL, RUNNING, COMPLETED, FAILED, ROLLED_BACK
    
    current_step_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    step_results: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    execution_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    triggered_by: Mapped[str] = mapped_column(String(100), default="AUTONOMOUS_ENGINE", nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SOARConnector(Base):
    """External security tool connector integration instance (Firewall, EDR, SIEM, IAM)."""
    __tablename__ = "soar_connectors"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    connector_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    connector_type: Mapped[str] = mapped_column(String(50), nullable=False) # FIREWALL, EDR, IAM, SIEM, TICKETING, SENSOR
    provider: Mapped[str] = mapped_column(String(50), default="AEGIVANTA_NATIVE", nullable=False) # PALO_ALTO, CROWDSTRIKE, OKTA, SERVICENOW, AWS, AEGIVANTA_NATIVE
    
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    health_status: Mapped[str] = mapped_column(String(30), default="HEALTHY", nullable=False) # HEALTHY, DEGRADED, OFFLINE
    latency_ms: Mapped[float] = mapped_column(Float, default=12.5, nullable=False)
    
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SOARKillSwitch(Base):
    """Emergency system-wide or tenant-level kill switch that forces instant manual containment."""
    __tablename__ = "soar_kill_switches"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
