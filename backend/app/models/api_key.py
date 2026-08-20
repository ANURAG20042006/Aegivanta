import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class ApiKeyScope(str, Enum):
    READ_TELEMETRY = "READ_TELEMETRY"
    WRITE_TELEMETRY = "WRITE_TELEMETRY"
    READ_INCIDENTS = "READ_INCIDENTS"
    WRITE_INCIDENTS = "WRITE_INCIDENTS"
    READ_THREAT_INTEL = "READ_THREAT_INTEL"
    RUN_HUNTS = "RUN_HUNTS"
    EXECUTE_RESPONSE = "EXECUTE_RESPONSE"
    READ_ANALYTICS = "READ_ANALYTICS"
    ADMIN = "ADMIN"


class ApiKey(Base):
    """Customer API Key representation. Never stores raw secrets."""
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # e.g., "sk_live_a1b2c3"
    hashed_secret: Mapped[str] = mapped_column(String(64), nullable=False)          # SHA-256 hex digest
    scopes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=False, default=list)  # List[str]
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    ip_restrictions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="api_keys")
