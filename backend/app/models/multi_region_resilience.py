"""
backend/app/models/multi_region_resilience.py
=============================================
Phase 42 Multi-Region Data Resilience, Active-Active Failover & Data Residency Models.
Covers Region Replication Clusters, Data Residency Boundaries, and Failover Events.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class RegionReplicationCluster(Base):
    """
    Multi-Region Database & Storage Replication Cluster Record.
    """
    __tablename__ = "region_replication_clusters"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    region_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # US_EAST_PRIMARY, EU_WEST_SECONDARY, APAC_SOUTH
    cluster_role: Mapped[str] = mapped_column(String(50), default="ACTIVE_PRIMARY", nullable=False)  # ACTIVE_PRIMARY, ACTIVE_STANDBY, SATELLITE_REPLICA
    health_status: Mapped[str] = mapped_column(String(20), default="ONLINE", nullable=False)  # ONLINE, DEGRADED, FAILOVER_ACTIVE
    replication_lag_ms: Mapped[Float] = mapped_column(Float, default=1.85, nullable=False)
    rpo_seconds: Mapped[Float] = mapped_column(Float, default=0.0, nullable=False)
    rto_seconds: Mapped[Float] = mapped_column(Float, default=1.5, nullable=False)

    last_sync: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DataResidencyBoundary(Base):
    """
    Sovereign Data Residency & Compliance Geo-Fence Policy Record.
    """
    __tablename__ = "data_residency_boundaries"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    boundary_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    compliance_standard: Mapped[str] = mapped_column(String(50), default="GDPR_EU_ONLY", nullable=False)  # GDPR_EU_ONLY, FEDRAMP_US_ONLY, APPI_JAPAN
    enforced_regions: Mapped[str] = mapped_column(String(255), default="EU_WEST_1,EU_CENTRAL_1", nullable=False)
    strict_egress_block: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class FailoverExecutionEvent(Base):
    """
    Autonomous or Operator-Initiated Regional Failover Event Record.
    """
    __tablename__ = "failover_execution_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    source_failing_region: Mapped[str] = mapped_column(String(50), nullable=False)
    target_failover_region: Mapped[str] = mapped_column(String(50), nullable=False)
    failover_trigger: Mapped[str] = mapped_column(String(50), default="AUTOMATIC_HEALTH_CHECK", nullable=False)  # AUTOMATIC_HEALTH_CHECK, OPERATOR_INITIATED
    switchover_duration_ms: Mapped[Float] = mapped_column(Float, default=420.0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS", nullable=False)  # SUCCESS, IN_PROGRESS, FAILED

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
