import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Incident(Base):
    """Incident entity model storing network traffic inspection results and threat metadata."""
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=False)
    destination_port: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(10), nullable=False)
    packet_length: Mapped[int] = mapped_column(Integer, nullable=False)
    flow_duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    attack_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    is_malicious: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(15), nullable=False, default="Low")  # Low, Medium, High, Critical
    
    model_name: Mapped[str] = mapped_column(String(50), nullable=False, default="Random Forest")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    feature_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
