import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SecurityPolicy(Base):
    """Centralized enterprise security policies per organization or tenant."""
    __tablename__ = "security_policies"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    require_mfa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    require_sso: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, default=480, nullable=False)  # 8 hours default
    max_concurrent_sessions: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    api_key_max_ttl_days: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    ip_allowlist: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {"ips": ["1.2.3.4/32"]}
    ip_denylist: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    password_min_length: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    require_password_special_char: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class CustomerSecurityEvent(Base):
    """Customer-facing auditable security events (logins, policy updates, API key changes, member invites)."""
    __tablename__ = "customer_security_events"
    __table_args__ = {"extend_existing": True}


    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # LOGIN_SUCCESS, MFA_ENABLED, POLICY_UPDATED, etc.
    severity: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False) # INFO, WARNING, CRITICAL
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    details_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
