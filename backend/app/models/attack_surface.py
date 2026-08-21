"""
backend/app/models/attack_surface.py
====================================
Phase 31 Attack Surface Management (ASM), Threat Exposure Management (CTEM) & External Recon Models.
Covers external asset inventories, open port mappings, dangling DNS / subdomain takeover risks,
dark web employee credential leaks, brand typosquatting, and Gartner 5-stage CTEM prioritization.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class ExternalAsset(Base):
    """
    Discovered External Asset (Domain, Subdomain, IP, Cloud Endpoint).
    Tracks open ports, SSL certificate expiry, cloud providers, and ASM risk scores.
    """
    __tablename__ = "external_assets"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    fqdn_or_ip: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(50), default="SUBDOMAIN", nullable=False)  # DOMAIN, SUBDOMAIN, IP_ADDRESS, S3_BUCKET
    primary_ip: Mapped[str] = mapped_column(String(45), default="198.51.100.1", nullable=False)
    asn_organization: Mapped[str] = mapped_column(String(100), default="AS16509 Amazon.com, Inc.", nullable=False)
    cloud_provider: Mapped[str] = mapped_column(String(50), default="AWS", nullable=False)  # AWS, AZURE, GCP, CLOUDFLARE, ON_PREM

    open_ports: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)  # [80, 443, 22, 3389]
    ssl_issuer: Mapped[str] = mapped_column(String(100), default="Let's Encrypt Authority X3", nullable=False)
    ssl_days_until_expiry: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    ssl_has_weak_ciphers: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, default=25.0, nullable=False)  # 0.0 - 100.0
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)  # ACTIVE, DORMANT, DECOMMISSIONED

    first_discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DanglingDNSRisk(Base):
    """
    Dangling DNS & Subdomain Takeover Vulnerability Record.
    Tracks CNAME pointers targeting abandoned cloud services (AWS S3, GitHub Pages, Azure Traffic Manager).
    """
    __tablename__ = "dangling_dns_risks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    subdomain: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    cname_target: Mapped[str] = mapped_column(String(255), nullable=False)
    target_service: Mapped[str] = mapped_column(String(100), default="AWS S3 Bucket", nullable=False)  # AWS_S3, GITHUB_PAGES, AZURE_APP, HEROKU

    takeover_risk_score: Mapped[float] = mapped_column(Float, default=90.0, nullable=False)
    is_takeover_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="VULNERABLE", nullable=False)  # VULNERABLE, MITIGATED, FALSE_POSITIVE

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DarkWebCredentialLeak(Base):
    """
    Dark Web & Breach Intelligence Record.
    Identifies leaked corporate credentials in hacker forums, Telegram channels, and pastebins.
    """
    __tablename__ = "darkweb_credential_leaks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    employee_email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    breach_source: Mapped[str] = mapped_column(String(100), default="Infostealer Malware Combo", nullable=False)
    password_hash_sample: Mapped[str] = mapped_column(String(64), nullable=False)
    is_plaintext_exposed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)  # CRITICAL, HIGH, MEDIUM
    is_remediated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class BrandImpersonationAlert(Base):
    """
    Brand Protection & Typosquatting Lookalike Domain Alert.
    Monitors punycode domains, lookalike spellings, and phishing lures impersonating the enterprise.
    """
    __tablename__ = "brand_impersonation_alerts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    impersonating_domain: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    levenshtein_similarity_score: Mapped[float] = mapped_column(Float, default=0.92, nullable=False)
    registrar_name: Mapped[str] = mapped_column(String(100), default="NameCheap, Inc.", nullable=False)

    has_active_mx_records: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Phishing active
    has_live_web_server: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    threat_status: Mapped[str] = mapped_column(String(30), default="ACTIVE_PHISHING_LURE", nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
