"""
backend/app/models/threat_intel_v2.py
=====================================
Phase 32 Cyber Threat Intelligence (CTI) 2.0, Threat Actor Profiling & STIX/TAXII 2.1 Models.
Covers nation-state and eCrime threat actors, Diamond Model attribution, automated TAXII feeds,
dynamic IOC confidence scoring with exponential time decay, and ATT&CK campaign heatmaps.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class ThreatActorProfile(Base):
    """
    Detailed Threat Actor Intelligence Profile.
    Includes Diamond Model data (Adversary, Capability, Infrastructure, Victim),
    targeted industries, primary MITRE ATT&CK techniques, and active campaign links.
    """
    __tablename__ = "threat_actor_profiles"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    actor_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # APT29, Volt Typhoon, LockBit
    aliases: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # ["Cozy Bear", "Nobelium", "Midnight Blizzard"]
    country_of_origin: Mapped[str] = mapped_column(String(100), default="Russia", nullable=False)
    actor_type: Mapped[str] = mapped_column(String(50), default="NATION_STATE", nullable=False)  # NATION_STATE, E_CRIME, HACKTIVIST
    primary_motivation: Mapped[str] = mapped_column(String(100), default="Espionage & IP Theft", nullable=False)
    sophistication_level: Mapped[str] = mapped_column(String(50), default="STRATEGIC", nullable=False)  # STRATEGIC, ADVANCED, INTERMEDIATE

    # Diamond Model Schema
    diamond_adversary: Mapped[str] = mapped_column(String(200), default="SVR Foreign Intelligence Service", nullable=False)
    diamond_capability: Mapped[str] = mapped_column(String(255), default="Custom Implants, Cloud Token Theft, Supply Chain Tampering", nullable=False)
    diamond_infrastructure: Mapped[str] = mapped_column(String(255), default="Compromised Residential Routers, Fast-Flux DNS, VPS Proxies", nullable=False)
    diamond_victimology: Mapped[str] = mapped_column(String(255), default="Government, Defense, Technology, Critical Infrastructure", nullable=False)

    targeted_sectors: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    primary_mitre_techniques: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # ["T1078", "T1195.002", "T1566"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class STIXFeedSource(Base):
    """
    STIX 2.1 & TAXII 2.1 Automated Threat Intelligence Feed Subscription.
    """
    __tablename__ = "stix_feed_sources"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    feed_name: Mapped[str] = mapped_column(String(100), nullable=False)  # CISA AIS Feed, AlienVault OTX, MITRE ATT&CK CTI
    taxii_server_url: Mapped[str] = mapped_column(String(255), nullable=False)
    collection_id: Mapped[str] = mapped_column(String(100), default="default-indicators", nullable=False)
    feed_format: Mapped[str] = mapped_column(String(30), default="STIX_2_1", nullable=False)

    poll_interval_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    feed_reputation_score: Mapped[float] = mapped_column(Float, default=95.0, nullable=False)  # 0 - 100
    auto_ingest_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    total_indicators_ingested: Mapped[int] = mapped_column(Integer, default=14200, nullable=False)
    last_poll_status: Mapped[str] = mapped_column(String(30), default="SUCCESS", nullable=False)
    last_polled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class CTIIndicatorRecord(Base):
    """
    CTI Indicator with Dynamic Confidence & Exponential Sighting Decay.
    """
    __tablename__ = "cti_indicator_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    indicator_type: Mapped[str] = mapped_column(String(30), default="IPV4", nullable=False)  # IPV4, DOMAIN, SHA256, URL
    indicator_value: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    stix_pattern: Mapped[str] = mapped_column(String(255), default="[ipv4-addr:value = '...']", nullable=False)
    threat_actor: Mapped[str] = mapped_column(String(100), default="Volt Typhoon", nullable=False)
    malware_family: Mapped[str] = mapped_column(String(100), default="KV-Botnet", nullable=False)

    initial_confidence_score: Mapped[float] = mapped_column(Float, default=90.0, nullable=False)
    current_confidence_score: Mapped[float] = mapped_column(Float, default=88.5, nullable=False)  # Decayed over time
    decay_halflife_days: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    sighting_count: Mapped[int] = mapped_column(Integer, default=8, nullable=False)

    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    first_observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_sighted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class CampaignHeatmapItem(Base):
    """
    MITRE ATT&CK Campaign Technique Heatmap Item.
    """
    __tablename__ = "campaign_heatmap_items"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    campaign_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    threat_actor: Mapped[str] = mapped_column(String(100), default="APT29", nullable=False)
    tactic_name: Mapped[str] = mapped_column(String(100), default="Initial Access", nullable=False)
    mitre_technique_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # T1195.002
    technique_name: Mapped[str] = mapped_column(String(150), default="Supply Chain Compromise", nullable=False)

    heat_level: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1 - 5 (Critical Heat)
    confidence_score: Mapped[float] = mapped_column(Float, default=95.0, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
