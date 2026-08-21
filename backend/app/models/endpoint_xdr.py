"""
backend/app/models/endpoint_xdr.py
==================================
Phase 22 Endpoint XDR & Zero-Trust Security Models.
Covers Normalized Endpoint Telemetry, EDR Detections, XDR Correlated Incidents,
Zero-Trust Device Posture, and Controlled Response Actions.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class EndpointTelemetryEvent(Base):
    """
    Normalized Endpoint Event Stream.
    Covers PROCESS, FILE, REGISTRY, AUTHENTICATION, NETWORK, PERSISTENCE, PRIVILEGE, and SYSTEM events.
    """
    __tablename__ = "endpoint_telemetry_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    sensor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # PROCESS, FILE, REGISTRY, AUTHENTICATION, NETWORK, PERSISTENCE, PRIVILEGE, SYSTEM
    process_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    process_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    process_cmdline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_process_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    user_account: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_hash_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    target_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    target_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    registry_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    severity: Mapped[str] = mapped_column(String(20), default="INFORMATIONAL", nullable=False) # CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
    raw_event: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class EndpointDetection(Base):
    """
    EDR Behavioral & Threat Detections.
    Detects Suspicious Processes, Credential Theft, Persistence, Privilege Escalation, Lateral Movement, and Ransomware.
    """
    __tablename__ = "endpoint_detections"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    sensor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    detection_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # SUSPICIOUS_PROCESS, CREDENTIAL_THEFT, PERSISTENCE_MECHANISM, PRIVILEGE_ESCALATION, LATERAL_MOVEMENT, RANSOMWARE_BEHAVIOR, ANOMALOUS_CMD
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    mitre_tactic: Mapped[str] = mapped_column(String(50), default="Execution", nullable=False)
    mitre_technique_id: Mapped[str] = mapped_column(String(30), default="T1059", nullable=False)

    confidence: Mapped[float] = mapped_column(Float, default=0.90, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    process_pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cmdline: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_involved: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_contained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class XDRCorrelationIncident(Base):
    """
    Cross-Domain XDR Multi-Source Incident Correlation.
    Correlates Endpoint + Network + Identity + Cloud + Threat Intelligence.
    """
    __tablename__ = "xdr_correlation_incidents"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    incident_title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False) # CRITICAL, HIGH, MEDIUM
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False) # OPEN, INVESTIGATING, CONTAINED, RESOLVED

    correlated_domains: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False) # ["ENDPOINT", "NETWORK", "IDENTITY", "CLOUD", "THREAT_INTEL"]
    evidence_graph: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    mitre_kill_chain: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    root_cause_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_actions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class ZeroTrustDevicePosture(Base):
    """
    Zero Trust Device Trust Score & Continuous Authorization Engine.
    """
    __tablename__ = "zero_trust_device_postures"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    sensor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    user_email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)

    device_trust_score: Mapped[float] = mapped_column(Float, default=85.0, nullable=False) # 0 - 100
    is_compliant: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    os_patch_status: Mapped[str] = mapped_column(String(30), default="UP_TO_DATE", nullable=False) # UP_TO_DATE, OUTDATED, CRITICAL_PATCH_MISSING
    edr_agent_health: Mapped[str] = mapped_column(String(30), default="HEALTHY", nullable=False) # HEALTHY, DEGRADED, MISSING
    disk_encryption_status: Mapped[str] = mapped_column(String(50), default="ENCRYPTED_BITLOCKER", nullable=False) # ENCRYPTED_BITLOCKER, ENCRYPTED_FILEVAULT, UNENCRYPTED
    firewall_status: Mapped[str] = mapped_column(String(30), default="ENABLED", nullable=False) # ENABLED, DISABLED

    access_decision: Mapped[str] = mapped_column(String(30), default="ALLOW", nullable=False) # ALLOW, STEP_UP_MFA, RESTRICT_ACCESS, QUARANTINE_DEVICE

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class EndpointResponseAction(Base):
    """
    Governed Endpoint & Zero Trust Response Actions.
    """
    __tablename__ = "endpoint_response_actions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    sensor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(200), nullable=False)

    action_type: Mapped[str] = mapped_column(String(50), nullable=False) # ISOLATE_ENDPOINT, TERMINATE_PROCESS, REVOKE_SESSION, RESET_CREDENTIALS, RESTORE_ISOLATION
    status: Mapped[str] = mapped_column(String(30), default="EXECUTED", nullable=False) # PENDING_APPROVAL, EXECUTED, ROLLED_BACK, REJECTED
    target_entity: Mapped[str] = mapped_column(String(200), nullable=False)
    approval_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    operator_id: Mapped[str] = mapped_column(String(100), default="SOC_OPERATOR_ADMIN", nullable=False)

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
