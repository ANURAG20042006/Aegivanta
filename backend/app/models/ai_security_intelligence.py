"""
backend/app/models/ai_security_intelligence.py
==============================================
Phase 20 AI/ML Security Intelligence Models.
Covers Model Governance, Lineage, Artifact Signatures, Drift Monitoring,
Adversarial Attack Defense Logs, and AI Copilot 2.0 Sessions.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class AIModelGovernance(Base):
    """
    Model Governance and Lifecycle Registry.
    Tracks model lineage, HMAC-SHA256 signatures, dataset provenance,
    performance evaluation metrics, and approval/rollback workflows.
    """
    __tablename__ = "ai_model_governance"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model_family: Mapped[str] = mapped_column(String(50), default="SUPERVISED_ENSEMBLE", nullable=False) # SUPERVISED, ANOMALY, BEHAVIORAL, ENSEMBLE
    framework: Mapped[str] = mapped_column(String(50), default="SCIKIT_LEARN", nullable=False) # SCIKIT_LEARN, XGBOOST, LIGHTGBM, PYTORCH

    stage: Mapped[str] = mapped_column(String(30), default="STAGING", nullable=False) # STAGING, CANARY, PRODUCTION, RETIRED, ROLLED_BACK
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    artifact_path: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    artifact_signature: Mapped[Optional[str]] = mapped_column(String(128), nullable=True) # HMAC-SHA256
    signature_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    training_dataset_name: Mapped[str] = mapped_column(String(150), default="CIC-IDS2017-Production-Split", nullable=False)
    training_dataset_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    training_samples_count: Mapped[int] = mapped_column(Integer, default=50000, nullable=False)
    features_list: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Evaluation metrics
    roc_auc: Mapped[float] = mapped_column(Float, default=0.985, nullable=False)
    precision_score: Mapped[float] = mapped_column(Float, default=0.962, nullable=False)
    recall_score: Mapped[float] = mapped_column(Float, default=0.954, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, default=0.958, nullable=False)
    log_loss_score: Mapped[float] = mapped_column(Float, default=0.082, nullable=False)
    p95_latency_ms: Mapped[float] = mapped_column(Float, default=14.5, nullable=False)

    # Lineage and governance
    parent_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), default="ML_PIPELINE", nullable=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    approval_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False) # PENDING, APPROVED, REJECTED
    approval_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    promoted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AIModelDriftRecord(Base):
    """
    Tracks data drift and prediction distribution shifts using
    Population Stability Index (PSI) and Kolmogorov-Smirnov statistics.
    """
    __tablename__ = "ai_model_drift_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    evaluation_window_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    samples_evaluated: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    overall_psi: Mapped[float] = mapped_column(Float, default=0.045, nullable=False) # PSI < 0.1 = No drift, 0.1-0.25 = Moderate, > 0.25 = Significant
    drift_status: Mapped[str] = mapped_column(String(30), default="NO_DRIFT", nullable=False) # NO_DRIFT, MODERATE_DRIFT, CRITICAL_DRIFT

    ks_statistic: Mapped[float] = mapped_column(Float, default=0.032, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, default=0.45, nullable=False)

    feature_drift_breakdown: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(255), default="Model distributions are statistically aligned with baseline.", nullable=False)


class AIAdversarialEvent(Base):
    """
    Logs detected and mitigated adversarial threats against Aegivanta's AI/ML engines,
    including training data poisoning, prompt injection attacks, malicious telemetry,
    and model extraction probes.
    """
    __tablename__ = "ai_adversarial_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    threat_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # DATA_POISONING, PROMPT_INJECTION, MODEL_EXTRACTION, MALICIOUS_TELEMETRY, ADVERSARIAL_INPUT
    source_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    target_component: Mapped[str] = mapped_column(String(100), default="AI_COPILOT", nullable=False)

    raw_payload_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    mitigation_action: Mapped[str] = mapped_column(String(50), default="SANITIZED_AND_BLOCKED", nullable=False) # BLOCKED, SANITIZED, QUANTIZED_JITTER, REJECTED_FROM_TRAINING
    confidence_penalty: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class AICopilotSession(Base):
    """
    Tracks AI Copilot 2.0 multi-turn analyst reasoning sessions,
    contextual incident investigations, and sanitized prompt histories.
    """
    __tablename__ = "ai_copilot_sessions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, default="SOC_ANALYST")
    incident_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)


    session_title: Mapped[str] = mapped_column(String(200), default="Incident Triage & Hunting Session", nullable=False)
    sanitized_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning_summary: Mapped[str] = mapped_column(Text, nullable=False)
    contributing_signals: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    recommended_playbook_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


    is_prompt_injection_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
