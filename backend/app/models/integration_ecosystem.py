"""
backend/app/models/integration_ecosystem.py
============================================
Phase 23 Enterprise Security Ecosystem Models.
Defines Connector Registry, Event Bus Contracts, Webhook Deliveries, and Failure Queue.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class IntegrationConnector(Base):
    """
    Connector Registry.
    Stores authenticated, versioned connector instances with encrypted configuration.
    """
    __tablename__ = "integration_connectors"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    connector_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # SIEM, SOAR, EDR, IAM, TICKETING, MESSAGING, EMAIL, WEBHOOK, THREAT_INTEL, CLOUD
    vendor: Mapped[str] = mapped_column(String(100), nullable=False) # Splunk, Sentinel, CrowdStrike, Okta, ServiceNow, Slack, PagerDuty, etc.
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ENABLED", nullable=False) # ENABLED, DISABLED, ERROR, RATE_LIMITED
    health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False) # 0–100
    auth_type: Mapped[str] = mapped_column(String(30), default="API_KEY", nullable=False) # API_KEY, OAUTH2, BASIC_AUTH, MTLS, HMAC_WEBHOOK
    config_encrypted: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False) # Encrypted credentials / secrets
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    retry_max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    backoff_base_seconds: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_successful_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class EventBusContract(Base):
    """
    Normalized Event Bus Record.
    Stores all inter-system events with normalized schema and routing metadata.
    """
    __tablename__ = "event_bus_contracts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True) # ALERT_CREATED, INCIDENT_CREATED, DETECTION_FIRED, IOC_MATCHED, RESPONSE_EXECUTED
    source_system: Mapped[str] = mapped_column(String(80), nullable=False) # aegivanta.edr, aegivanta.siem, aegivanta.soar
    target_connector_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0", nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL", nullable=False) # CRITICAL, HIGH, NORMAL, LOW
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)


class WebhookDelivery(Base):
    """
    Webhook Delivery Tracking with signing, replay protection, and dead-letter support.
    """
    __tablename__ = "webhook_deliveries"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    connector_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    endpoint_url: Mapped[str] = mapped_column(String(500), nullable=False)
    hmac_signature: Mapped[str] = mapped_column(String(128), nullable=False) # HMAC-SHA256 of payload + timestamp
    replay_nonce: Mapped[str] = mapped_column(String(64), nullable=False) # Prevents replay attacks
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False) # PENDING, DELIVERED, FAILED, DEAD_LETTER
    http_status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_dead_letter: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
