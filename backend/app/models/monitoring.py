"""
backend/app/models/monitoring.py
================================
Continuous Asset Monitoring and Time-Series Health Observations.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


class MonitoringCheck(Base):
    """Configuration and current state for continuous monitoring of protected assets."""
    __tablename__ = "monitoring_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("protected_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    monitor_type = Column(String(30), nullable=False, default="HTTP")  # HTTP, HTTPS, TCP_PORT, DNS, PING
    target_url = Column(String(512), nullable=False)
    expected_status_code = Column(Integer, default=200)
    timeout_seconds = Column(Float, default=5.0)
    interval_seconds = Column(Integer, default=60)
    is_enabled = Column(Boolean, default=True, index=True)

    # Health & State Tracking
    health_state = Column(String(20), default="HEALTHY", index=True)  # HEALTHY, DEGRADED, DOWN, MAINTENANCE
    consecutive_failures = Column(Integer, default=0)
    last_check_at = Column(DateTime, nullable=True)
    last_status_code = Column(Integer, nullable=True)
    last_response_time_ms = Column(Float, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    
    # Advanced Network & TLS Metrics
    tls_expiry_days = Column(Integer, nullable=True)
    dns_resolved_ip = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("ProtectedAsset", backref="monitoring_checks")
    history = relationship("MonitoringHistory", back_populates="check", cascade="all, delete-orphan")


class MonitoringHistory(Base):
    """Historical time-series observation log for monitoring checks."""
    __tablename__ = "monitoring_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    check_id = Column(String(36), ForeignKey("monitoring_checks.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(String(36), ForeignKey("protected_assets.id", ondelete="CASCADE"), nullable=False, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=False)
    is_success = Column(Boolean, default=True, index=True)
    error_message = Column(Text, nullable=True)

    # Diagnostics
    dns_lookup_ms = Column(Float, nullable=True)
    tls_handshake_ms = Column(Float, nullable=True)
    cert_days_left = Column(Integer, nullable=True)

    # Relationships
    check = relationship("MonitoringCheck", back_populates="history")
