"""
backend/app/models/edge_security_fabric.py
=========================================
Phase 41 Global Distributed Edge Security & Regional Ingestion Fabric Models.
Covers Edge PoP Nodes, Edge Inspection Policies, and Regional Ingestion Routes.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class GlobalEdgePoPNode(Base):
    """
    Global Edge Point of Presence (PoP) Ingestion Node Record.
    """
    __tablename__ = "global_edge_pop_nodes"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    region_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # US_EAST_VA, EU_CENTRAL_FRA, AP_SOUTHEAST_SIN
    pop_location_name: Mapped[str] = mapped_column(String(100), nullable=False)
    edge_status: Mapped[str] = mapped_column(String(20), default="HEALTHY", nullable=False)  # HEALTHY, DEGRADED, DRAINING
    throughput_gbps: Mapped[Float] = mapped_column(Float, default=42.5, nullable=False)
    active_connections: Mapped[int] = mapped_column(Integer, default=125000, nullable=False)
    latency_ms: Mapped[Float] = mapped_column(Float, default=4.2, nullable=False)

    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class EdgeInspectionPolicy(Base):
    """
    Edge-Side Security Inspection & DDoS Scrubbing Policy Record.
    """
    __tablename__ = "edge_inspection_policies"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    policy_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    inspection_mode: Mapped[str] = mapped_column(String(50), default="INLINE_BLOCK", nullable=False)  # INLINE_BLOCK, PASS_THROUGH, SCRUB_DDOS
    edge_rate_limit_rps: Mapped[int] = mapped_column(Integer, default=50000, nullable=False)
    geo_fence_action: Mapped[str] = mapped_column(String(20), default="CHALLENGE", nullable=False)  # ALLOW, BLOCK, CHALLENGE
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class RegionalIngestionRoute(Base):
    """
    Regional Ingestion & Edge-to-Core WAN Replication Route Record.
    """
    __tablename__ = "regional_ingestion_routes"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    source_region: Mapped[str] = mapped_column(String(50), nullable=False)
    target_core_cluster: Mapped[str] = mapped_column(String(100), nullable=False)
    routing_protocol: Mapped[str] = mapped_column(String(50), default="WIREGUARD_MTLS", nullable=False)
    replication_lag_ms: Mapped[Float] = mapped_column(Float, default=1.45, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
