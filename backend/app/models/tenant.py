import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class TenantRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    SECURITY_ANALYST = "SECURITY_ANALYST"
    RESPONDER = "RESPONDER"
    VIEWER = "VIEWER"
    BILLING_ADMIN = "BILLING_ADMIN"
    API_ADMIN = "API_ADMIN"


class Organization(Base):
    """Top-level customer organization holding multiple tenants/workspaces."""
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    billing_email: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_tier: Mapped[str] = mapped_column(String(30), nullable=False, default="FREE")  # FREE, PROFESSIONAL, BUSINESS, ENTERPRISE
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")    # ACTIVE, SUSPENDED, TRIAL
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    tenants = relationship("Tenant", back_populates="organization", cascade="all, delete-orphan")
    memberships = relationship("TenantMembership", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    integrations = relationship("CustomerIntegration", back_populates="organization", cascade="all, delete-orphan")


class Tenant(Base):
    """Isolated tenant / workspace boundary under an organization."""
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    environment_type: Mapped[str] = mapped_column(String(30), nullable=False, default="production")  # production, staging, lab
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="tenants")
    memberships = relationship("TenantMembership", back_populates="tenant", cascade="all, delete-orphan")
    settings = relationship("TenantSettings", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="tenant", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="tenant", cascade="all, delete-orphan")


class TenantMembership(Base):
    """Association of a User with an Organization & Tenant with a specific role."""
    __tablename__ = "tenant_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="SECURITY_ANALYST")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, INVITED, SUSPENDED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="tenant_memberships")
    organization = relationship("Organization", back_populates="memberships")
    tenant = relationship("Tenant", back_populates="memberships")


class TenantSettings(Base):
    """Configurable security, compliance, and retention settings per tenant."""
    __tablename__ = "tenant_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    retention_days_hot: Mapped[int] = mapped_column(nullable=False, default=30)
    retention_days_warm: Mapped[int] = mapped_column(nullable=False, default=90)
    retention_days_cold: Mapped[int] = mapped_column(nullable=False, default=365)
    require_mfa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ip_allowlist: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notification_webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="settings")
