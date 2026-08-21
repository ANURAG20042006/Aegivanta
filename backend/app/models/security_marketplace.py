"""
backend/app/models/security_marketplace.py
==========================================
Phase 44 Security Marketplace & Ecosystem Package Manager Models.
Covers Marketplace Packages, Installed Extensions, and Package Reviews.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class MarketplacePackage(Base):
    """
    Certified or Community Security Extension Package.
    """
    __tablename__ = "marketplace_packages"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="global-catalog")

    package_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    package_type: Mapped[str] = mapped_column(String(50), default="DETECTION_PACK", nullable=False)  # DETECTION_PACK, SOAR_PLAYBOOK, CONNECTOR_ADAPTER, AI_AGENT_SKILL
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    author: Mapped[str] = mapped_column(String(255), default="Aegivanta Core Team", nullable=False)
    verified_publisher: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    signature_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    installs_count: Mapped[int] = mapped_column(Integer, default=1250, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PUBLISHED", nullable=False)  # PUBLISHED, DEPRECATED

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class InstalledExtension(Base):
    """
    Tenant-Installed Security Extension.
    """
    __tablename__ = "installed_extensions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    package_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    installed_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    auto_update: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class PackageReviewRating(Base):
    """
    Ecosystem Package Community Rating & Review.
    """
    __tablename__ = "package_review_ratings"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    package_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    reviewer_name: Mapped[str] = mapped_column(String(255), default="SecOps Lead", nullable=False)
    rating_stars: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    review_comment: Mapped[str] = mapped_column(Text, default="Flawless integration with high fidelity alerts.", nullable=False)

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
