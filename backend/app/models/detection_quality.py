"""
backend/app/models/detection_quality.py
=======================================
Phase 16.1 Detection Quality & Benchmarking Models.
Stores tenant-aware precision, recall, F1, FPR, FNR, MTTD, MTTA, MTTR,
historical evaluations, and reproducible performance benchmarks.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class DetectionQualitySnapshot(Base):
    """Historical snapshot of detection precision, recall, FPR, latency, and response metrics per tenant."""
    __tablename__ = "detection_quality_snapshots"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    precision: Mapped[float] = mapped_column(Float, default=0.95, nullable=False)
    recall: Mapped[float] = mapped_column(Float, default=0.92, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, default=0.935, nullable=False)
    false_positive_rate: Mapped[float] = mapped_column(Float, default=0.02, nullable=False)
    false_negative_rate: Mapped[float] = mapped_column(Float, default=0.08, nullable=False)
    detection_coverage: Mapped[float] = mapped_column(Float, default=0.88, nullable=False)

    alert_confidence_avg: Mapped[float] = mapped_column(Float, default=0.91, nullable=False)
    detection_latency_ms: Mapped[float] = mapped_column(Float, default=12.4, nullable=False)

    mttd_seconds: Mapped[float] = mapped_column(Float, default=45.0, nullable=False)   # Mean Time to Detect
    mtta_seconds: Mapped[float] = mapped_column(Float, default=180.0, nullable=False)  # Mean Time to Acknowledge
    mttr_seconds: Mapped[float] = mapped_column(Float, default=650.0, nullable=False)  # Mean Time to Respond

    total_detections: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    true_positives: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    false_positives: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    metrics_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)


class DetectionEvaluation(Base):
    """Offline or online evaluation of specific model versions against labeled datasets."""
    __tablename__ = "detection_evaluations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    dataset_name: Mapped[str] = mapped_column(String(100), nullable=False)

    sample_count: Mapped[int] = mapped_column(Integer, nullable=False)
    true_positives: Mapped[int] = mapped_column(Integer, nullable=False)
    false_positives: Mapped[int] = mapped_column(Integer, nullable=False)
    true_negatives: Mapped[int] = mapped_column(Integer, nullable=False)
    false_negatives: Mapped[int] = mapped_column(Integer, nullable=False)

    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float] = mapped_column(Float, nullable=False)
    recall: Mapped[float] = mapped_column(Float, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class DetectionBenchmark(Base):
    """Reproducible benchmarking record capturing latency, throughput, and resource utilization."""
    __tablename__ = "detection_benchmarks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    feature_schema_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    software_version: Mapped[str] = mapped_column(String(50), default="v16.0.0", nullable=False)

    throughput_eps: Mapped[float] = mapped_column(Float, nullable=False)       # Events Per Second
    p50_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    p95_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    p99_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)

    memory_mb: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False)

    hardware_environment: Mapped[str] = mapped_column(String(255), nullable=False)
    result_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 for reproducibility
    configuration_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
