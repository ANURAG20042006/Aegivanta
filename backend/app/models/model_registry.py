import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


VALID_MODEL_STATUSES = ["CANDIDATE", "ACTIVE", "REJECTED", "ARCHIVED", "ROLLED_BACK"]


class ModelRegistry(Base):
    """
    Model Registry storing trained ML/DL classifier versioning,
    lifecycle status (CANDIDATE -> ACTIVE / REJECTED -> ARCHIVED / ROLLED_BACK),
    multi-metric performance scores, and artifact paths.
    """
    __tablename__ = "model_registry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    model_type: Mapped[str] = mapped_column(String(30), nullable=False)  # Classical, Boosting, DeepLearning
    status: Mapped[str] = mapped_column(String(20), default="CANDIDATE", nullable=False)
    
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)
    precision_score: Mapped[float] = mapped_column(Float, nullable=False)
    recall_score: Mapped[float] = mapped_column(Float, nullable=False)
    roc_auc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.45)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    artifact_path: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(30), default="schema-v1.0", nullable=False)
    preprocessing_version: Mapped[str] = mapped_column(String(50), default="split_first_smote_inside_folds_only", nullable=False)
    
    trained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    promoted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    previous_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promotion_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confusion_matrix: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
