"""
backend/app/models/threat_intel.py
==================================
Threat Intelligence Indicators of Compromise (IOC) and Ingestion Feeds.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from backend.app.database import Base


class ThreatIndicator(Base):
    """Normalized repository of threat intelligence indicators (IOCs)."""
    __tablename__ = "threat_indicators"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ioc_type = Column(String(20), nullable=False, index=True)  # ipv4, ipv6, domain, url, sha256, md5
    raw_value = Column(String(512), nullable=False)
    normalized_value = Column(String(512), nullable=False, index=True)
    
    threat_type = Column(String(50), nullable=False, default="malicious_host", index=True)  # c2, botnet, scanner, phishing, bruteforce
    severity = Column(String(20), nullable=False, default="HIGH", index=True)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    confidence = Column(Float, default=0.85)  # 0.0 to 1.0
    source = Column(String(100), nullable=False, default="Local_SOC", index=True)
    description = Column(Text, nullable=True)
    
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    tags = Column(JSON, default=list)  # list of tags e.g. ["patator", "c2", "mirai"]
    is_active = Column(Boolean, default=True, index=True)
    lifecycle_status = Column(String(30), default="ACTIVE", index=True)  # ACTIVE, EXPIRED, ARCHIVED, REVOKED
    hit_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ThreatFeed(Base):
    """Configuration and sync state for external/internal threat intelligence feeds."""
    __tablename__ = "threat_feeds"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feed_name = Column(String(100), unique=True, nullable=False)
    provider_type = Column(String(50), nullable=False, default="generic_json")  # generic_json, generic_csv, static_list, misp
    feed_url = Column(String(512), nullable=True)
    poll_interval_hours = Column(Integer, default=24)
    
    last_synced_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(30), default="IDLE")  # IDLE, SUCCESS, FAILED, RUNNING
    last_error = Column(Text, nullable=True)
    indicators_imported = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
