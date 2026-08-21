"""
backend/app/models/developer_webhooks.py
========================================
Phase 45 Developer Platform, Public Versioned API & Webhooks Engine Models.
Covers Developer API Keys, Webhook Subscriptions, and Delivery Logs.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class DeveloperApiKey(Base):
    """
    Public Developer API Key with granular RBAC scopes.
    """
    __tablename__ = "developer_api_keys"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    key_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(32), default="aeg_live_", nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    scopes: Mapped[str] = mapped_column(String(255), default="telemetry:read,alerts:write", nullable=False)
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class WebhookSubscription(Base):
    """
    Real-Time Event Webhook Subscription.
    """
    __tablename__ = "webhook_subscriptions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    endpoint_url: Mapped[str] = mapped_column(String(512), nullable=False)
    subscribed_events: Mapped[str] = mapped_column(String(255), default="alert.created,threat.blocked", nullable=False)
    secret_token: Mapped[str] = mapped_column(String(64), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    retry_count_max: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class WebhookDeliveryLog(Base):
    """
    Immutable Webhook Event Delivery Audit Record.
    """
    __tablename__ = "webhook_delivery_logs"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    subscription_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), default="alert.created", nullable=False)
    payload_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    response_status: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=45.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DELIVERED", nullable=False)  # DELIVERED, FAILED, DLQ_BUFFERED

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
