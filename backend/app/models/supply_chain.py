"""
backend/app/models/supply_chain.py
==================================
Phase 29 Supply Chain Security, SBOM 2.0 & Code-to-Cloud Governance Models.
Covers Software Bill of Materials (CycloneDX/SPDX), OpenVEX Exploitability Statements,
SLSA Level 3 Provenance & Build Attestations, and CI/CD Security Gatekeeper Policies.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class SBOMCatalogItem(Base):
    """
    Software Bill of Materials (SBOM 2.0) Dependency Component.
    Tracks direct and transitive third-party dependencies across Python, Node.js, Go, and Maven.
    """
    __tablename__ = "sbom_catalog_items"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    package_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    purl: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # pkg:pypi/cryptography@42.0.5
    ecosystem: Mapped[str] = mapped_column(String(30), nullable=False)  # PYPI, NPM, GOLANG, MAVEN, DEBIAN

    is_direct_dependency: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    license_spdx_id: Mapped[str] = mapped_column(String(50), default="Apache-2.0", nullable=False)
    is_copyleft: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    vulnerability_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_cve_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_cve_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cve_identifiers: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    supplier_name: Mapped[str] = mapped_column(String(100), default="OpenSource Community", nullable=False)
    sha256_checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class VEXStatement(Base):
    """
    OpenVEX & CSAF Vulnerability Exploitability eXchange (VEX) Statement.
    Records exploitability determinations (e.g. NOT_AFFECTED, FIXED, UNDER_INVESTIGATION).
    """
    __tablename__ = "vex_statements"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    vulnerability_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # CVE-2026-10492
    product_purl: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)  # NOT_AFFECTED, AFFECTED, FIXED, UNDER_INVESTIGATION

    justification: Mapped[str] = mapped_column(String(100), default="Vulnerable code is not invoked by execution path", nullable=False)
    impact_statement: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(100), default="Aegivanta SupplyChain Engine", nullable=False)

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SLSAPipelineAttestation(Base):
    """
    SLSA Level 3 & NIST SSDF Provenance Attestation Record.
    Validates hermetic builds, signed provenance, and builder identity.
    """
    __tablename__ = "slsa_pipeline_attestations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    artifact_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    artifact_digest: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    slsa_level: Mapped[str] = mapped_column(String(20), default="SLSA_LEVEL_3", nullable=False)  # SLSA_LEVEL_1, SLSA_LEVEL_2, SLSA_LEVEL_3

    builder_id: Mapped[str] = mapped_column(String(200), default="https://github.com/actions/runner@v2", nullable=False)
    build_invocation_id: Mapped[str] = mapped_column(String(100), nullable=False)
    cosign_signature: Mapped[str] = mapped_column(Text, nullable=False)
    is_signature_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    source_repo_uri: Mapped[str] = mapped_column(String(200), default="https://github.com/aegivanta/core", nullable=False)
    source_commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    materials: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class PipelineSecurityGate(Base):
    """
    CI/CD Gatekeeper Security Policy Definition & Evaluation Rule.
    Enforces security thresholds before builds can deploy to staging/production.
    """
    __tablename__ = "pipeline_security_gates"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    gate_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_environment: Mapped[str] = mapped_column(String(30), default="PRODUCTION", nullable=False)
    enforcement_mode: Mapped[str] = mapped_column(String(20), default="BLOCKING", nullable=False)  # BLOCKING, AUDIT_ONLY

    max_critical_cves: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_high_cves: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    require_slsa_level_3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    disallow_copyleft_licenses: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    require_secret_scan_clean: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
