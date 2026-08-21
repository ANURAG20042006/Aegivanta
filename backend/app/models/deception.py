"""
backend/app/models/deception.py
===============================
Phase 33 Deception Technology, Honeypots & Active Adversary Engagement Models (MITRE Engage / D3FEND).
Covers low/high interaction honeypot fleets (SSH Cowrie, Web, SMB, Database, Kerberoast SPNs),
canary token generation (AWS API Keys, Doc webhooks, DNS beacons), real-time adversary interaction ledgers,
and endpoint lure deployments.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class HoneypotNode(Base):
    """
    Deployed Honeypot Decoy Node.
    Emulates vulnerable services (SSH, WordPress admin, MySQL, Windows SMB share, AD Kerberoast SPN).
    """
    __tablename__ = "honeypot_nodes"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    node_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    decoy_type: Mapped[str] = mapped_column(String(50), default="SSH_COWRIE", nullable=False)  # SSH_COWRIE, WEB_PORTAL, SMB_FILE_SHARE, DATABASE, AD_KERBEROAST
    internal_ip: Mapped[str] = mapped_column(String(45), default="10.0.12.50", nullable=False)
    vlan_segment: Mapped[str] = mapped_column(String(50), default="DMZ-DECEPTION-VLAN", nullable=False)
    emulation_profile: Mapped[str] = mapped_column(String(100), default="Ubuntu 22.04 LTS OpenSSH 8.9p1", nullable=False)

    interaction_level: Mapped[str] = mapped_column(String(30), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH
    total_hits_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="LISTENING", nullable=False)  # LISTENING, ENGAGED, OFFLINE

    deployed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class CanaryToken(Base):
    """
    Traceable Canary Token Object.
    Canary AWS API keys, Doc webhooks, DNS canary domains, and fake database passwords.
    """
    __tablename__ = "canary_tokens"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    token_type: Mapped[str] = mapped_column(String(50), default="AWS_API_KEY", nullable=False)  # AWS_API_KEY, WEBHOOK_DOC, DNS_BEACON, KUBECONFIG, DB_CREDENTIAL
    token_name: Mapped[str] = mapped_column(String(100), nullable=False)
    token_value_preview: Mapped[str] = mapped_column(String(100), default="AKIAIOSFODNN7EXAMPLE", nullable=False)
    trigger_url_or_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    placement_description: Mapped[str] = mapped_column(String(255), default="Placed in /root/.aws/credentials on bastion-01", nullable=False)

    times_triggered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class DeceptionInteractionEvent(Base):
    """
    Adversary Deception Hit & Interaction Ledger.
    Records attacker keystrokes, credential attempts, and payload executions.
    """
    __tablename__ = "deception_interaction_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    source_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    attacker_asn: Mapped[str] = mapped_column(String(100), default="AS14061 DigitalOcean, LLC", nullable=False)
    target_decoy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    interaction_type: Mapped[str] = mapped_column(String(50), default="AUTH_ATTEMPT", nullable=False)  # AUTH_ATTEMPT, COMMAND_EXEC, FILE_DOWNLOAD, CANARY_TRIGGER

    captured_payload_or_command: Mapped[str] = mapped_column(Text, nullable=False)
    mitre_engage_activity: Mapped[str] = mapped_column(String(50), default="EAC0004_EXPOSE", nullable=False)  # EAC0004_EXPOSE, EAC0012_REDIRECT, EAC0018_ELICIT
    fidelity_confidence: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)  # 100% true-positive
    containment_action_taken: Mapped[str] = mapped_column(String(50), default="IP_ISOLATED_BY_SOAR", nullable=False)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class EndpointLureDeployment(Base):
    """
    Endpoint Deception Lure Distribution State.
    Injected credentials in LSASS, fake browser cookies, and network share lures on corporate endpoints.
    """
    __tablename__ = "endpoint_lure_deployments"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    endpoint_hostname: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lure_type: Mapped[str] = mapped_column(String(50), default="SAVED_CREDENTIAL", nullable=False)  # SAVED_CREDENTIAL, CANARY_FILE, BROWSER_COOKIE, HONEY_SPN
    target_honey_user: Mapped[str] = mapped_column(String(100), default="svc_backup_admin", nullable=False)
    deployment_status: Mapped[str] = mapped_column(String(30), default="INJECTED_ACTIVE", nullable=False)  # INJECTED_ACTIVE, REMOVED, VERIFYING

    last_verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
