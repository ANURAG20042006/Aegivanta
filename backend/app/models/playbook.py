"""
backend/app/models/playbook.py
==============================
Automated Playbook Executions and Dry-Run Simulation Audit Logs with RBAC tracking.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class PlaybookExecution(Base):
    """Execution record for automated security playbooks with mandatory audit trail."""
    __tablename__ = "playbook_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_id = Column(String(36), default=lambda: str(uuid.uuid4()), index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    playbook_name = Column(String(100), nullable=False)  # e.g., IP_CONTAINMENT_PLAYBOOK, VLAN_ISOLATION_PLAYBOOK
    action_type = Column(String(50), nullable=False)  # BLOCK_IP, QUARANTINE_VLAN, NOTIFY_WEBHOOK, ISOLATE_HOST
    is_dry_run = Column(Boolean, default=True, nullable=False, index=True)  # True = Simulation; False = Real Execution
    target_entity = Column(String(255), nullable=False)  # Target IP, Subnet, or Hostname
    parameters = Column(JSON, default=dict)
    
    status = Column(String(30), default="SIMULATED_SUCCESS", index=True)  # SIMULATED_SUCCESS, EXECUTED_SUCCESS, FAILED, DENIED
    executed_by = Column(String(100), default="automated_system")  # Username
    actor_role = Column(String(30), default="analyst")  # Role at execution time
    authorization_decision = Column(String(30), default="APPROVED")  # APPROVED, DENIED_INSUFFICIENT_PERMISSIONS
    execution_log = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    incident = relationship("Incident", backref="playbook_executions")
