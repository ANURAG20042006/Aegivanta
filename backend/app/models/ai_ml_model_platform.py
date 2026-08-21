"""
backend/app/models/ai_ml_model_platform.py
==========================================
Phase 48 — Global AI/ML Model Platform, Registry, Drift Monitoring & Adversarial Defenses.

Models:
- MLModelRegistryV2      : Versioned enterprise ML model registry with full lineage
- MLModelDriftRecord     : Statistical drift monitoring record per model version
- AdversarialAttackEvent : Adversarial attack detection and defense event log
"""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, JSON
)
from backend.app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MLModelRegistryV2(Base):
    """Enterprise versioned ML model registry with full lifecycle and lineage tracking."""
    __tablename__ = "ml_model_registry_v2"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")

    model_name = Column(String(200), nullable=False, default="CatBoost-ThreatClassifier")
    model_version = Column(String(50), nullable=False, default="v3.2.1")
    model_type = Column(String(80), nullable=False, default="GRADIENT_BOOSTING")  # e.g. GNN, TRANSFORMER, SVM
    model_family = Column(String(80), nullable=False, default="THREAT_CLASSIFICATION")
    framework = Column(String(60), nullable=False, default="catboost")  # catboost, xgboost, pytorch, sklearn
    serving_endpoint = Column(String(500), nullable=True)
    artifact_path = Column(String(500), nullable=True)
    artifact_sha256 = Column(String(64), nullable=True)

    # Quality metrics
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    inference_p99_ms = Column(Float, nullable=True, default=3.2)

    # Lifecycle
    status = Column(String(30), nullable=False, default="ACTIVE")  # ACTIVE, SHADOW, DEPRECATED, CHAMPION
    is_champion = Column(Boolean, nullable=False, default=False)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    retired_at = Column(DateTime(timezone=True), nullable=True)

    # Lineage
    training_dataset_ref = Column(String(500), nullable=True)
    parent_model_version = Column(String(50), nullable=True)
    feature_schema_json = Column(JSON, nullable=False, default=list)
    hyperparameters_json = Column(JSON, nullable=False, default=dict)
    tags_json = Column(JSON, nullable=False, default=list)

    registered_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<MLModelRegistryV2 {self.model_name}@{self.model_version} [{self.status}]>"


class MLModelDriftRecord(Base):
    """Statistical drift monitoring record for a specific model version."""
    __tablename__ = "ml_model_drift_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")
    model_id = Column(String(36), nullable=False, index=True)
    model_name = Column(String(200), nullable=False, default="CatBoost-ThreatClassifier")
    model_version = Column(String(50), nullable=False, default="v3.2.1")

    # Drift metrics
    data_drift_score = Column(Float, nullable=False, default=0.02)   # PSI or KS stat
    concept_drift_score = Column(Float, nullable=False, default=0.01)
    prediction_drift_score = Column(Float, nullable=False, default=0.03)
    drift_severity = Column(String(20), nullable=False, default="NONE")  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    drift_method = Column(String(50), nullable=False, default="PSI")  # PSI, KS_TEST, EVIDENTLY

    # Feature-level drift
    feature_drift_breakdown_json = Column(JSON, nullable=False, default=dict)
    reference_window_start = Column(DateTime(timezone=True), nullable=True)
    reference_window_end = Column(DateTime(timezone=True), nullable=True)
    detection_window_start = Column(DateTime(timezone=True), nullable=True)
    detection_window_end = Column(DateTime(timezone=True), nullable=True)

    # Alerts & Actions
    alert_triggered = Column(Boolean, nullable=False, default=False)
    auto_retrain_triggered = Column(Boolean, nullable=False, default=False)
    remediation_action = Column(String(100), nullable=True)

    detected_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<MLModelDriftRecord {self.model_name}@{self.model_version} severity={self.drift_severity}>"


class AdversarialAttackEvent(Base):
    """Adversarial attack detection and defense event against ML models."""
    __tablename__ = "adversarial_attack_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")
    model_id = Column(String(36), nullable=False, index=True)
    model_name = Column(String(200), nullable=False, default="CatBoost-ThreatClassifier")

    attack_type = Column(String(80), nullable=False, default="EVASION")
    # EVASION, POISONING, MODEL_EXTRACTION, MEMBERSHIP_INFERENCE, PROMPT_INJECTION
    attack_severity = Column(String(20), nullable=False, default="MEDIUM")
    attack_vector_json = Column(JSON, nullable=False, default=dict)
    confidence_score = Column(Float, nullable=False, default=0.94)

    # Defense outcome
    defense_mechanism = Column(String(100), nullable=False, default="ADVERSARIAL_INPUT_DETECTION")
    blocked = Column(Boolean, nullable=False, default=True)
    confidence_after_defense = Column(Float, nullable=True)
    defense_latency_ms = Column(Float, nullable=True, default=1.2)

    source_ip = Column(String(45), nullable=True)
    raw_payload_hash = Column(String(64), nullable=True)
    detected_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<AdversarialAttackEvent {self.attack_type} severity={self.attack_severity} blocked={self.blocked}>"
