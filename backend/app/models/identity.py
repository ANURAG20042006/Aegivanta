import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class IdentityProvider(Base):
    """Enterprise SSO Identity Provider (OIDC / SAML 2.0) configuration per organization."""
    __tablename__ = "identity_providers"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_type: Mapped[str] = mapped_column(String(20), nullable=False)  # OIDC, SAML
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)
    client_secret_encrypted: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    discovery_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # For OIDC
    sso_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)        # For SAML
    entity_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)      # SAML Issuer/EntityID
    x509_cert: Mapped[Optional[str]] = mapped_column(Text, nullable=True)             # SAML Certificate
    domain_hints: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)         # {"domains": ["acme.com"]}
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_enforced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # Requires all users to use SSO
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class UserSession(Base):
    """Tracks active user sessions with IP, device fingerprints, and revocation state."""
    __tablename__ = "user_sessions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False)
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class MFAEnrollment(Base):
    """User TOTP MFA enrollment and emergency recovery codes."""
    __tablename__ = "mfa_enrollments"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    mfa_type: Mapped[str] = mapped_column(String(20), default="TOTP", nullable=False)
    encrypted_secret: Mapped[str] = mapped_column(String(500), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recovery_codes_hash_json: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
