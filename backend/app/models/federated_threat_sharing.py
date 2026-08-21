"""
backend/app/models/federated_threat_sharing.py
==============================================
Phase 40 Privacy-Preserving Threat Intelligence & Federated IOC Exchange Models.
Covers Federated Exchange Nodes, Anonymized Indicators with Differential Privacy,
and Homomorphic Encrypted Match Queries.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class FederatedIOCExchangeNode(Base):
    """
    Federated Exchange Peer Node Record.
    """
    __tablename__ = "federated_ioc_exchange_nodes"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    node_pseudonym: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    trust_tier: Mapped[str] = mapped_column(String(50), default="VERIFIED_ENTERPRISE", nullable=False)  # VERIFIED_ENTERPRISE, GOV_CERT, RESEARCH_PARTNER
    consensus_weight: Mapped[Float] = mapped_column(Float, default=1.0, nullable=False)
    public_key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, SUSPENDED

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class FederatedThreatIndicator(Base):
    """
    Anonymized Federated Threat Indicator with Differential Privacy.
    """
    __tablename__ = "federated_threat_indicators"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    anonymized_indicator_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    threat_classification: Mapped[str] = mapped_column(String(100), default="APT_C2_INFRASTRUCTURE", nullable=False)
    differential_privacy_epsilon: Mapped[Float] = mapped_column(Float, default=0.5, nullable=False)  # Epsilon parameter
    confidence_consensus_score: Mapped[Float] = mapped_column(Float, default=0.96, nullable=False)
    peer_validations_count: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    syndication_status: Mapped[str] = mapped_column(String(30), default="CONSENSUS_REACHED", nullable=False)  # CONSENSUS_REACHED, VALIDATING, REJECTED

    shared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class HomomorphicMatchQuery(Base):
    """
    Encrypted Homomorphic / Blind Match Search Record.
    """
    __tablename__ = "homomorphic_match_queries"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    encrypted_query_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    blind_match_status: Mapped[str] = mapped_column(String(30), default="BLIND_MATCH_FOUND", nullable=False)  # BLIND_MATCH_FOUND, NO_MATCH
    execution_time_ms: Mapped[Float] = mapped_column(Float, default=2.15, nullable=False)

    queried_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
