"""
backend/app/models/dlp_security.py
==================================
Phase 35 Data Loss Prevention (DLP), Enterprise Data Classification & Tokenization Models (DSPM / Privacy 2.0).
Covers PCI-DSS (Luhn verified credit cards), PII (SSNs, Passports), HIPAA medical codes, API keys,
multi-channel DLP incidents, format-preserving encryption (FPE) tokenization vaults, and shadow data discovery.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class DLPInspectionPolicy(Base):
    """
    DLP Sensitive Data Inspection & Classification Rule.
    Enforces regex, keyword matching, and Luhn checksum validation.
    """
    __tablename__ = "dlp_inspection_policies"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    policy_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    data_category: Mapped[str] = mapped_column(String(50), default="PCI_CARD", nullable=False)  # PCI_CARD, PII_SSN, HIPAA_HEALTH, SECRET_KEY, SOURCE_CODE
    sensitivity_tier: Mapped[str] = mapped_column(String(30), default="RESTRICTED_HIGH_RISK", nullable=False)  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED_HIGH_RISK

    regex_pattern: Mapped[str] = mapped_column(Text, nullable=False)
    context_keywords: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["credit", "card", "pan", "cvv"], nullable=False)
    enforcement_action: Mapped[str] = mapped_column(String(50), default="BLOCK_TRANSMISSION", nullable=False)  # BLOCK_TRANSMISSION, REDACT_MASK, QUARANTINE_ENCRYPT, AUDIT_ALERT

    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_violations_intercepted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DLPIncidentEvent(Base):
    """
    DLP Exfiltration & Transmission Violation Record.
    Captures attempted egress of confidential records across API, Cloud, and Web.
    """
    __tablename__ = "dlp_incident_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    source_identity: Mapped[str] = mapped_column(String(100), default="sarah.connor@corp.internal", nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="API_GATEWAY", nullable=False)  # API_GATEWAY, CLOUD_STORAGE, EMAIL_COLLAB, WEB_EGRESS
    target_destination: Mapped[str] = mapped_column(String(255), default="external-webhook.partner-api.com", nullable=False)

    matched_policy_name: Mapped[str] = mapped_column(String(100), default="PCI-DSS Credit Card Exfiltration Guard", nullable=False)
    data_category: Mapped[str] = mapped_column(String(50), default="PCI_CARD", nullable=False)
    masked_sample_snippet: Mapped[str] = mapped_column(String(255), default="4111-XXXX-XXXX-1111", nullable=False)
    violations_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    enforcement_action_taken: Mapped[str] = mapped_column(String(50), default="BLOCK_TRANSMISSION", nullable=False)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class TokenizedDataVault(Base):
    """
    Reversible Cryptographic Tokenization Vault (FPE / AES-256-GCM).
    Stores surrogate tokens replacing raw sensitive credit cards and SSNs.
    """
    __tablename__ = "tokenized_data_vault"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    token_identifier: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    surrogate_token_value: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. TKN-4111-9824-7712-1111
    token_format: Mapped[str] = mapped_column(String(50), default="FPE_CREDIT_CARD", nullable=False)  # FPE_CREDIT_CARD, FPE_SSN, HASH_EMAIL

    cipher_algorithm: Mapped[str] = mapped_column(String(50), default="AES_256_GCM", nullable=False)
    encrypted_blob_payload: Mapped[Text] = mapped_column(Text, nullable=False)
    authorized_roles: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["admin", "compliance_officer"], nullable=False)

    times_detokenized: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_detokenized_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class ShadowDataStore(Base):
    """
    DSPM Shadow Data Store Discovery Object.
    Identifies unencrypted cloud buckets, database tables, and sensitive file shares.
    """
    __tablename__ = "shadow_data_stores"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    resource_uri: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # s3://prod-analytics-exports, azure://backups/pii
    storage_provider: Mapped[str] = mapped_column(String(50), default="AWS_S3", nullable=False)  # AWS_S3, AZURE_BLOB, GCP_GCS, RDS_POSTGRES
    discovered_sensitive_records_count: Mapped[int] = mapped_column(Integer, default=14200, nullable=False)
    detected_data_categories: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["PII_SSN", "PCI_CARD"], nullable=False)

    encryption_state: Mapped[str] = mapped_column(String(50), default="UNENCRYPTED_PUBLIC", nullable=False)  # UNENCRYPTED_PUBLIC, SSE_KMS, CLIENT_ENCRYPTED
    risk_level: Mapped[str] = mapped_column(String(20), default="CRITICAL", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
