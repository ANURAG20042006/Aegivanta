import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


VALID_ALERT_SEVERITIES = ["info", "low", "medium", "high", "critical"]
VALID_ALERT_STATUSES = ["new", "acknowledged", "investigating", "resolved", "dismissed"]


class Alert(Base):
    """
    Alert entity model storing detected security anomalies,
    risk scores, source/destination telemetry, and incident associations.
    """
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id: Mapped[str] = mapped_column(String(50), default=lambda: f"ALT-{uuid.uuid4().hex[:8].upper()}", nullable=False, unique=True, index=True)
    
    asset_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("protected_assets.id", ondelete="SET NULL"), nullable=True, index=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(15), nullable=False, default="medium", index=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="ML_ENGINE:CatBoost")
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    source_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    destination_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str] = mapped_column(String(10), nullable=False, default="TCP")
    packet_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    flow_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    attack_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new", index=True)
    explanation: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
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
