"""
backend/app/models/investigation.py
===================================
Automated Incident Investigation, Evidence Aggregation, and MITRE ATT&CK Stage Mapping.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Investigation(Base):
    """Automated incident investigation summary and ATT&CK chain analysis."""
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    asset_id = Column(String(36), ForeignKey("protected_assets.id", ondelete="SET NULL"), nullable=True, index=True)

    status = Column(String(30), default="COMPLETED", index=True)  # OPEN, IN_PROGRESS, COMPLETED
    summary = Column(Text, nullable=False)
    findings = Column(JSON, default=dict)
    
    # MITRE ATT&CK Framework Mapping
    attack_chain_stage = Column(String(50), default="RECONNAISSANCE", index=True)
    # RECONNAISSANCE, INITIAL_ACCESS, EXECUTION, PERSISTENCE, LATERAL_MOVEMENT, EXFILTRATION, IMPACT
    confidence_score = Column(Float, default=0.90)  # 0.0 to 1.0
    recommended_actions = Column(JSON, default=list)  # list of suggested analyst actions

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    incident = relationship("Incident", backref="investigation")
    asset = relationship("ProtectedAsset")
    evidence = relationship("InvestigationEvidence", back_populates="investigation", cascade="all, delete-orphan")


class InvestigationEvidence(Base):
    """Traceable empirical evidence item associated with an investigation."""
    __tablename__ = "investigation_evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    evidence_type = Column(String(40), nullable=False, index=True)
    # ALERT, FLOW_TELEMETRY, IOC_MATCH, BEHAVIORAL_ANOMALY, HEALTH_DEGRADATION, TIMELINE_EVENT
    reference_id = Column(String(100), nullable=True)  # ID of referenced alert/event/indicator
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default=dict)

    # Relationships
    investigation = relationship("Investigation", back_populates="evidence")
