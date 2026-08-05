import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class ModelRegistry(Base):
    """Model registry storing trained ML/DL classifier evaluation metrics and serialized artifact locations."""
    __tablename__ = "model_registry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    model_type: Mapped[str] = mapped_column(String(30), nullable=False)  # Classical, Boosting, DeepLearning
    
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)
    precision_score: Mapped[float] = mapped_column(Float, nullable=False)
    recall_score: Mapped[float] = mapped_column(Float, nullable=False)
    roc_auc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    artifact_path: Mapped[str] = mapped_column(String(255), nullable=False)
    trained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    confusion_matrix: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
