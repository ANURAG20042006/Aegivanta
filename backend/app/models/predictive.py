"""
backend/app/models/predictive.py
================================
SQLAlchemy Models for Predictive Security Analytics and Forecasting.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class RiskForecast(Base):
    """Stores asset-specific risk trend forecasts (e.g. 24h, 7d)."""
    __tablename__ = "risk_forecasts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String, ForeignKey("protected_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_type = Column(String(50), nullable=False)  # 24H, 7D
    forecast_horizon = Column(String(50), default="24_HOURS")
    predicted_score = Column(Float, nullable=False)  # 0.0 - 100.0
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    baseline_score = Column(Float, nullable=False)
    model_family = Column(String(50), default="phase3_predictive", nullable=False)
    model_version = Column(String(50), default="forecast-v1", nullable=False)
    explanation = Column(JSON, nullable=True)  # Factors influencing the forecast
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    asset = relationship("ProtectedAsset", backref="risk_forecasts")


class AlertVolumeForecast(Base):
    """Stores enterprise-wide projected alert volume trends."""
    __tablename__ = "alert_volume_forecasts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    forecast_window = Column(String(50), nullable=False)  # NEXT_6H, NEXT_24H, NEXT_7D
    predicted_alert_count = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    model_family = Column(String(50), default="phase3_predictive", nullable=False)
    model_version = Column(String(50), default="volume-forecast-v1", nullable=False)
    historical_reference_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
