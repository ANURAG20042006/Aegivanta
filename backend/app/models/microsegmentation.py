"""
backend/app/models/microsegmentation.py
=======================================
Phase 36 Microsegmentation, Software-Defined Perimeter (SDP) & Zero Trust Network Access (ZTNA 2.0) Models.
Covers SDP Connectors, L4/L7 Microsegmentation Policies, Identity-Bound ZTNA Sessions,
and Lateral Movement Interception Alerts.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class ZTNAConnectorNode(Base):
    """
    Software-Defined Perimeter (SDP) / ZTNA 2.0 Edge Gateway Node.
    Terminates mutual-TLS WireGuard/IPsec overlay tunnels from authenticated zero-trust clients.
    """
    __tablename__ = "ztna_connector_nodes"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    connector_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(50), default="us-east-1", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ONLINE", nullable=False)  # ONLINE, DEGRADED, OFFLINE

    public_ip: Mapped[str] = mapped_column(String(45), default="52.14.88.102", nullable=False)
    private_overlay_cidr: Mapped[str] = mapped_column(String(50), default="100.64.0.0/16", nullable=False)
    active_client_sessions_count: Mapped[int] = mapped_column(Integer, default=142, nullable=False)
    total_bytes_tunneled_gb: Mapped[Float] = mapped_column(Float, default=1840.5, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="v36.0.0", nullable=False)

    last_heartbeat_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class MicrosegmentationPolicy(Base):
    """
    Layer 4 & Layer 7 Microsegmentation Policy.
    Restricts inter-workload, inter-VPC, and service-to-service communication.
    """
    __tablename__ = "microsegmentation_policies"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    policy_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_segment: Mapped[str] = mapped_column(String(100), default="PAYMENT_GATEWAY_VPC", nullable=False)
    destination_segment: Mapped[str] = mapped_column(String(100), default="CORE_DATABASE_CLUSTER", nullable=False)

    protocol_port: Mapped[str] = mapped_column(String(50), default="TCP/5432", nullable=False)
    enforcement_action: Mapped[str] = mapped_column(String(50), default="ALLOW_ENCRYPTED_TUNNEL", nullable=False)  # ALLOW_ENCRYPTED_TUNNEL, DENY_ISOLATE, REQUIRE_MFA_STEPUP
    min_device_trust_score: Mapped[int] = mapped_column(Integer, default=80, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_evaluated_flows: Mapped[int] = mapped_column(Integer, default=84200, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ZTNAAccessSession(Base):
    """
    Identity-Bound Zero Trust Network Access Client Session.
    Binds authenticated identity, device certificate attestation, and dynamic trust score.
    """
    __tablename__ = "ztna_access_sessions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    user_email: Mapped[str] = mapped_column(String(100), default="alex.mercer@corp.internal", nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(100), default="MAC-CORP-M3-8821", nullable=False)
    connector_node_name: Mapped[str] = mapped_column(String(100), default="ztna-gw-us-east-1", nullable=False)

    client_overlay_ip: Mapped[str] = mapped_column(String(45), default="100.64.12.84", nullable=False)
    target_application: Mapped[str] = mapped_column(String(255), default="k8s-prod-api.internal:6443", nullable=False)
    current_trust_score: Mapped[int] = mapped_column(Integer, default=94, nullable=False)  # 0 to 100
    session_status: Mapped[str] = mapped_column(String(30), default="ACTIVE_TUNNEL", nullable=False)  # ACTIVE_TUNNEL, REVOKED_ANOMALY, EXPIRED

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class LateralMovementBlockedAlert(Base):
    """
    Lateral Movement Interception & Microsegmentation Breach Alert.
    Triggers when an unauthorized internal workload attempts to traverse isolated segment boundaries.
    """
    __tablename__ = "lateral_movement_blocked_alerts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    source_workload: Mapped[str] = mapped_column(String(100), default="dev-runner-pod-4", nullable=False)
    source_segment: Mapped[str] = mapped_column(String(100), default="DEVELOPMENT_SANDBOX", nullable=False)
    target_workload: Mapped[str] = mapped_column(String(100), default="vault-kms-cluster-01", nullable=False)
    target_segment: Mapped[str] = mapped_column(String(100), default="RESTRICTED_KEY_VAULT", nullable=False)

    attempted_port_protocol: Mapped[str] = mapped_column(String(50), default="TCP/8200", nullable=False)
    interception_action: Mapped[str] = mapped_column(String(50), default="BLOCKED_AND_ISOLATED", nullable=False)
    threat_classification: Mapped[str] = mapped_column(String(100), default="UNAUTHORIZED_LATERAL_PIVOT", nullable=False)

    blocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
