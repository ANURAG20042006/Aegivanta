"""
backend/app/models/llm_security.py
==================================
Phase 30 AI/LLM Application Security, LLM-as-a-Target Defense & Shadow AI Governance Models.
Defends against OWASP Top 10 for LLMs (LLM01 Prompt Injection, LLM02 Sensitive Data Disclosure,
LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 RAG/Vector DB Poisoning).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class LLMGuardrailPolicy(Base):
    """
    LLM Guardrail Firewall Policy Configuration.
    Controls prompt inspection sensitivity, PII redaction, output sanitization, and token rate limits.
    """
    __tablename__ = "llm_guardrail_policies"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    policy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_model_endpoint: Mapped[str] = mapped_column(String(150), default="ALL_LLM_ENDPOINTS", nullable=False)
    enforcement_mode: Mapped[str] = mapped_column(String(20), default="BLOCKING", nullable=False)  # BLOCKING, AUDIT_ONLY

    block_prompt_injection: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prompt_injection_threshold: Mapped[float] = mapped_column(Float, default=0.75, nullable=False)

    redact_pii: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    block_system_prompt_leakage: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sanitize_output_xss: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_tokens_per_prompt: Mapped[int] = mapped_column(Integer, default=4096, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class LLMSecurityEvent(Base):
    """
    Audit ledger for LLM threat events (Prompt Injections, Jailbreaks, PII Leaks, System Prompt Extraction).
    """
    __tablename__ = "llm_security_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    owasp_category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # LLM01, LLM02, LLM07, LLM08
    threat_title: Mapped[str] = mapped_column(String(150), nullable=False)
    source_user_principal: Mapped[str] = mapped_column(String(100), default="anonymous_user", nullable=False)
    source_ip: Mapped[str] = mapped_column(String(45), default="127.0.0.1", nullable=False)

    raw_prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    redacted_prompt_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    action_taken: Mapped[str] = mapped_column(String(50), default="PROMPT_BLOCKED_AND_LOGGED", nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ShadowAIDiscoveryRecord(Base):
    """
    Shadow AI Discovery & Employee Usage Record.
    Tracks unauthorized consumer GenAI applications (ChatGPT, Claude, Midjourney, Perplexity).
    """
    __tablename__ = "shadow_ai_discovery_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    ai_tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # ChatGPT, Claude, Midjourney
    category: Mapped[str] = mapped_column(String(50), default="GENERATIVE_AI_CHATBOT", nullable=False)
    user_principal: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    endpoint_hostname: Mapped[str] = mapped_column(String(100), nullable=False)

    data_volume_mb: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)
    risk_rating: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    is_corporate_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class VectorDBAuditRecord(Base):
    """
    RAG & Vector Database Security Audit Record.
    Scans Pinecone, Weaviate, Qdrant, Chroma, and pgvector instances for tenant isolation and poisoning.
    """
    __tablename__ = "vectordb_audit_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    db_type: Mapped[str] = mapped_column(String(50), default="CHROMA_DB", nullable=False)  # PINECONE, WEAVIATE, CHROMA, QDRANT
    collection_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    total_embeddings_count: Mapped[int] = mapped_column(Integer, default=12500, nullable=False)

    is_tenant_isolated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_unencrypted_embeddings: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pii_exposure_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    poisoning_anomaly_score: Mapped[float] = mapped_column(Float, default=0.04, nullable=False)  # 0.0 to 1.0

    audit_status: Mapped[str] = mapped_column(String(30), default="SECURE", nullable=False)  # SECURE, WARNING, CRITICAL
    audited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
