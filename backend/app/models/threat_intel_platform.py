"""
backend/app/models/threat_intel_platform.py
===========================================
Phase 18 Threat Intelligence Platform Models:
Threat Actors, Campaigns, Malware Families, Indicator Sightings,
and Multi-Dimensional IOC Intelligence Relationships.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class ThreatActor(Base):
    """Normalized threat actor and adversary group profiling entity."""
    __tablename__ = "threat_actors"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    actor_type: Mapped[str] = mapped_column(String(50), default="NATION_STATE", nullable=False)  # NATION_STATE, CYBERCRIMINAL, HACKTIVIST, APT
    origin_country: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    motivation: Mapped[str] = mapped_column(String(100), default="ESPIONAGE", nullable=False)  # ESPIONAGE, FINANCIAL, SABOTAGE, EXTORTION
    sophistication: Mapped[str] = mapped_column(String(30), default="HIGH", nullable=False)  # LOW, MEDIUM, HIGH, EXPERT

    confidence_score: Mapped[float] = mapped_column(Float, default=0.90, nullable=False)
    ttp_list: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)  # e.g. ["T1059", "T1021", "T1110"]
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    first_observed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_observed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ThreatCampaign(Base):
    """Malicious campaign tracking coordinated attack operations."""
    __tablename__ = "threat_campaigns"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("threat_actors.id", ondelete="SET NULL"), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objective: Mapped[str] = mapped_column(String(150), default="Data Exfiltration", nullable=False)

    malware_families: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    targeted_sectors: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    targeted_countries: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)

    confidence: Mapped[float] = mapped_column(Float, default=0.88, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class MalwareFamily(Base):
    """Malware strain and toolset classification entity."""
    __tablename__ = "malware_families"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    malware_type: Mapped[str] = mapped_column(String(50), default="RANSOMWARE", nullable=False)  # RANSOMWARE, TROJAN, LOADER, C2_AGENT, SPYWARE
    capabilities: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    signature_hashes: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class IndicatorSighting(Base):
    """Empirical occurrence sighting of a threat indicator across customer network sensors."""
    __tablename__ = "indicator_sightings"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    indicator_id: Mapped[str] = mapped_column(String(36), ForeignKey("threat_indicators.id", ondelete="CASCADE"), nullable=False, index=True)

    sensor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    source_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    destination_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    destination_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    is_confirmed_threat: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    recorded_by: Mapped[str] = mapped_column(String(100), default="TELEMETRY_ENGINE", nullable=False)

    sighted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
