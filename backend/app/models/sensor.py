import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Sensor(Base):
    """Customer telemetry collection sensor / agent deployed on customer infrastructure."""
    __tablename__ = "sensors"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    os_type: Mapped[str] = mapped_column(String(50), nullable=False)  # linux, windows, macos, k8s
    sensor_type: Mapped[str] = mapped_column(String(30), default="ENDPOINT_EDR", nullable=False)  # NETWORK_TAP, ENDPOINT_EDR, K8S_DAEMONSET, CLOUD_AUDIT
    sensor_version: Mapped[str] = mapped_column(String(30), nullable=False, default="6.0.0")
    target_version: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    upgrade_status: Mapped[str] = mapped_column(String(30), default="UP_TO_DATE", nullable=False)  # UP_TO_DATE, PENDING_UPGRADE, UPGRADING, FAILED
    status: Mapped[str] = mapped_column(String(20), default="ONLINE", nullable=False)  # ONLINE, DEGRADED, OFFLINE, REVOKED
    health_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 0 - 100 derived health index
    enrollment_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_token_rotation: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    offline_buffer_events: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    revocation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="sensors")
