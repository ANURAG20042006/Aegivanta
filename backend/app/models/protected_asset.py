import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


VALID_ASSET_TYPES = ["website", "api", "server", "database", "endpoint", "network", "other"]
VALID_ENVIRONMENTS = ["production", "staging", "development"]
VALID_CRITICALITIES = ["low", "medium", "high", "critical"]
VALID_ASSET_STATUSES = ["active", "degraded", "compromised", "maintenance", "inactive"]


class ProtectedAsset(Base):
    """
    Protected Asset model representing monitored infrastructure
    (Websites, APIs, Servers, Databases, Endpoints, Network segments).
    """
    __tablename__ = "protected_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)
    
    asset_type: Mapped[str] = mapped_column(String(30), nullable=False, default="website", index=True)
    environment: Mapped[str] = mapped_column(String(30), nullable=False, default="production", index=True)
    criticality: Mapped[str] = mapped_column(String(20), nullable=False, default="medium", index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True, default=dict)
    
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
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
