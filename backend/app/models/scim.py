import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SCIMConfiguration(Base):
    """SCIM 2.0 provisioning configuration for enterprise Identity Providers."""
    __tablename__ = "scim_configurations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    bearer_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    default_role: Mapped[str] = mapped_column(String(30), default="SECURITY_ANALYST", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class SCIMProvisioningEvent(Base):
    """Immutable audit trail of all SCIM provisioning operations (user create, update, delete)."""
    __tablename__ = "scim_provisioning_events"
    __table_args__ = {"extend_existing": True}


    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # CREATE_USER, UPDATE_USER, DEACTIVATE_USER, DELETE_USER
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    details_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
