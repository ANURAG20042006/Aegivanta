"""
backend/app/models/behavioral.py
================================
Asset Behavioral Baselines and Explainable Anomaly Events.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


class BehavioralBaseline(Base):
    """Rolling statistical baseline for protected asset network telemetry dimensions."""
    __tablename__ = "behavioral_baselines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("protected_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(60), nullable=False, index=True)  # packet_rate, request_rate, destination_diversity, error_rate_pct, byte_volume
    
    window_hours = Column(Integer, default=24)
    baseline_mean = Column(Float, nullable=False, default=0.0)
    baseline_std = Column(Float, nullable=False, default=1.0)
    min_val = Column(Float, default=0.0)
    max_val = Column(Float, default=0.0)
    sample_count = Column(Integer, default=0)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("ProtectedAsset", backref="behavioral_baselines")


class AnomalyEvent(Base):
    """Explainable behavioral anomaly detection event."""
    __tablename__ = "anomaly_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("protected_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_name = Column(String(60), nullable=False, index=True)
    observed_value = Column(Float, nullable=False)
    baseline_mean = Column(Float, nullable=False)
    baseline_std = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False)
    
    anomaly_score = Column(Float, nullable=False)  # 0.0 to 100.0
    severity = Column(String(20), default="MEDIUM", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    explanation = Column(Text, nullable=False)  # Deterministic English rationale
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, SUPPRESSED, RESOLVED

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    asset = relationship("ProtectedAsset", backref="anomaly_events")
