"""
backend/app/models/identity.py
==============================
Phase 5 & Phase 28 Enterprise Identity, Access Management & Zero Trust 2.0 Models.
Covers Identity Providers (SAML/OIDC), User Sessions, MFA/Passkeys,
Privileged Access Management (PAM) JIT Elevations, Identity Threat Detection & Response (ITDR),
and Identity Posture Scorecards.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
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
    is_enforced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Requires all users to use SSO
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


class PAMSessionElevation(Base):
    """
    Privileged Access Management (PAM) Just-in-Time (JIT) Elevation Requests.
    Enforces time-bounded privilege escalation, mandatory approvals, and session recording.
    """
    __tablename__ = "pam_session_elevations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    target_role: Mapped[str] = mapped_column(String(50), nullable=False)  # SUPER_ADMIN, SEC_OPS_ADMIN, CLUSTER_ADMIN, BREAK_GLASS_ADMIN
    target_resource: Mapped[str] = mapped_column(String(200), nullable=False)  # PROD_K8S_CLUSTER, VAULT_DATABASE_MASTER, PROD_AWS_ROOT

    justification: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, APPROVED, ACTIVE, EXPIRED, REVOKED, REJECTED

    approved_by: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    session_audit_log: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class IdentityThreatDetection(Base):
    """
    Identity Threat Detection & Response (ITDR) Detections.
    Detects MFA push fatigue attacks, password spraying, impossible travel, and golden ticket kerberos attacks.
    """
    __tablename__ = "identity_threat_detections"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    threat_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # MFA_FATIGUE, PASSWORD_SPRAYING, IMPOSSIBLE_TRAVEL, CREDENTIAL_STUFFING, KERBEROASTING
    target_username: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    source_ip: Mapped[str] = mapped_column(String(50), nullable=False)
    geo_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)  # CRITICAL, HIGH, MEDIUM
    risk_score: Mapped[float] = mapped_column(Float, default=80.0, nullable=False)
    mitre_attack_id: Mapped[str] = mapped_column(String(30), default="T1110", nullable=False)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    action_taken: Mapped[str] = mapped_column(String(100), default="STEP_UP_MFA_ENFORCED", nullable=False)
    evidence_details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class PasskeyCredential(Base):
    """
    FIDO2 / WebAuthn Biometric & Hardware Security Key Passkeys.
    """
    __tablename__ = "passkey_credentials"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    credential_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    public_key_pem: Mapped[str] = mapped_column(Text, nullable=False)
    device_nickname: Mapped[str] = mapped_column(String(100), default="YubiKey 5C NFC", nullable=False)
    aaguid: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    sign_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_backup_eligible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class IdentityScorecard(Base):
    """
    Identity Governance & Risk Posture Record per user identity.
    """
    __tablename__ = "identity_scorecards"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False)

    identity_risk_score: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)  # 0 to 100
    risk_tier: Mapped[str] = mapped_column(String(20), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL

    is_dormant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_days_ago: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    passkey_registered: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_excessive_privileges: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    assigned_roles: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
