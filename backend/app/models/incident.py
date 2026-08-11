import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


VALID_INCIDENT_STATUSES = ["DETECTED", "TRIAGED", "INVESTIGATING", "CONTAINED", "RESOLVED", "CLOSED"]

ALLOWED_STATE_TRANSITIONS: Dict[str, List[str]] = {
    "DETECTED": ["TRIAGED"],
    "TRIAGED": ["INVESTIGATING", "CLOSED"],
    "INVESTIGATING": ["CONTAINED", "RESOLVED"],
    "CONTAINED": ["RESOLVED"],
    "RESOLVED": ["CLOSED"],
    "CLOSED": []
}


def is_valid_state_transition(current_status: str, next_status: str) -> bool:
    """Validates allowed state machine transitions for incident lifecycle."""
    curr = current_status.upper()
    nxt = next_status.upper()
    if curr == nxt:
        return True
    allowed = ALLOWED_STATE_TRANSITIONS.get(curr, [])
    return nxt in allowed


class Incident(Base):
    """
    Incident entity model storing network threat detection,
    lifecycle state transitions (DETECTED -> TRIAGED -> INVESTIGATING -> CONTAINED -> RESOLVED -> CLOSED),
    analyst assignments, remediation actions, and model versioning.
    """
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id: Mapped[str] = mapped_column(String(50), default=lambda: f"ALT-{uuid.uuid4().hex[:8].upper()}", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="DETECTED", nullable=False, index=True)
    
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
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="xgboost-v1.0")
    
    analyst: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    remediation_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    triaged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    feature_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
