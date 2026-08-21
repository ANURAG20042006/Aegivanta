"""
backend/app/models/security_automation_studio.py
================================================
Phase 46 Security Automation Studio (Visual Playbook Builder & SOAR Workflow Canvas) Models.
Covers Automation Playbooks, Execution Runs, and Pre-built Templates.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class AutomationPlaybook(Base):
    """
    Visual Automation Playbook DAG Definition.
    """
    __tablename__ = "automation_playbooks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(50), default="ON_ALERT", nullable=False)  # ON_ALERT, ON_SCHEDULE, ON_WEBHOOK
    canvas_graph_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, DRAFT, PAUSED
    executions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class PlaybookExecutionRun(Base):
    """
    Audit and runtime state execution ledger for an automation playbook.
    """
    __tablename__ = "playbook_execution_runs"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    playbook_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    playbook_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_event: Mapped[str] = mapped_column(String(100), default="ALERT_CRITICAL", nullable=False)
    current_step: Mapped[str] = mapped_column(String(100), default="FINAL_NOTIFICATION", nullable=False)
    step_results_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)  # COMPLETED, RUNNING, FAILED, AWAITING_APPROVAL
    duration_ms: Mapped[float] = mapped_column(Float, default=145.0, nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class PlaybookTemplate(Base):
    """
    Turnkey Enterprise Security Automation Template.
    """
    __tablename__ = "playbook_templates"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="INCIDENT_RESPONSE", nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    default_graph_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
