import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class DetectionRule(Base):
    """Detection-as-Code versioned rule entity supporting MITRE mapping and marketplace distribution."""
    __tablename__ = "detection_rules"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)  # e.g. AEG-R-2026-001
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    author: Mapped[str] = mapped_column(String(100), default="Aegivanta Research", nullable=False)
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="ENABLED", nullable=False, index=True)  # ENABLED, DISABLED, TESTING, DEPRECATED
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mitre_attack_mappings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # {"tactics": [...], "techniques": [...]}
    rule_dsl: Mapped[dict] = mapped_column(JSON, nullable=False)  # {"field": "protocol", "op": "eq", "value": "TCP"}
    false_positive_guidance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    investigation_recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    is_marketplace: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
