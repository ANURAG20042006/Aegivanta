"""
backend/app/models/data_governance_dsar.py
==========================================
Phase 43 Enterprise Data Governance, Lineage, Legal Hold & DSAR Privacy Models.
Covers Data Lineage Records, Legal Hold Orders, and DSAR Privacy Requests.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class DataLineageRecord(Base):
    """
    Data Asset Provenance & Processing Lineage Record.
    """
    __tablename__ = "data_lineage_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    data_asset_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pipeline_stage: Mapped[str] = mapped_column(String(50), default="SENSOR_INGRESS", nullable=False)  # SENSOR_INGRESS, EDGE_SCRUB, ML_FEATURE_STORE, COLD_ARCHIVE
    transform_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    upstream_asset_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    record_count: Mapped[int] = mapped_column(Integer, default=500000, nullable=False)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class LegalHoldOrder(Base):
    """
    Forensic Evidence Legal Hold Custody Record.
    """
    __tablename__ = "legal_hold_orders"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    matter_reference: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    custodian_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_pattern: Mapped[str] = mapped_column(String(255), default="CASE_FORENSICS_*", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE_HOLD", nullable=False)  # ACTIVE_HOLD, RELEASED
    frozen_artifact_count: Mapped[int] = mapped_column(Integer, default=42, nullable=False)

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DSARPrivacyRequest(Base):
    """
    GDPR / CCPA Data Subject Access Request (DSAR) Record.
    """
    __tablename__ = "dsar_privacy_requests"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    requester_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(50), default="RIGHT_OF_ACCESS_EXPORT", nullable=False)  # RIGHT_OF_ACCESS_EXPORT, RIGHT_TO_ERASURE_DELETE, RECTIFICATION
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)  # PENDING_APPROVAL, PROCESSING, COMPLETED
    discovered_records_count: Mapped[int] = mapped_column(Integer, default=128, nullable=False)
    completion_certificate_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
