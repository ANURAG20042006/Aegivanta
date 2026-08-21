"""
backend/app/models/predictive_intel.py
======================================
Phase 39 Predictive Security Intelligence & Emerging Threat Forecasting Models.
Covers Threat Vector Forecasts, Adversarial Blast Radius Simulations,
and Global Threat Horizon Indicators.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class PredictiveThreatForecast(Base):
    """
    Predictive Threat Vector Forecast Record.
    Tracks forecasted attack vectors, probability scores, horizons, and model versioning.
    """
    __tablename__ = "predictive_threat_forecasts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    threat_vector_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_asset_category: Mapped[str] = mapped_column(String(100), default="Kubernetes Production Clusters", nullable=False)
    probability_score: Mapped[Float] = mapped_column(Float, default=0.88, nullable=False)  # 0.00 to 1.00
    predicted_impact_severity: Mapped[str] = mapped_column(String(20), default="CRITICAL", nullable=False)  # CRITICAL, HIGH, MEDIUM
    forecast_horizon: Mapped[str] = mapped_column(String(20), default="30_DAYS", nullable=False)  # 30_DAYS, 60_DAYS, 90_DAYS

    confidence_score: Mapped[Float] = mapped_column(Float, default=0.92, nullable=False)
    evidence_features_summary: Mapped[Text] = mapped_column(Text, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), default="v39.1.0-forecaster", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class AdversarialVectorSimulation(Base):
    """
    Adversarial Attack Vector Simulation.
    Simulates hypothetical multi-stage breach escalation and blast-radius expansion.
    """
    __tablename__ = "adversarial_vector_simulations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    threat_scenario_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    initial_access_vector: Mapped[str] = mapped_column(String(100), default="Supply Chain Compromise (PyPI)", nullable=False)
    predicted_escalation_pathway: Mapped[Text] = mapped_column(Text, nullable=False)
    estimated_blast_radius_nodes: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    mitigation_directive: Mapped[Text] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ThreatHorizonIndicator(Base):
    """
    Global Threat Horizon & Trend Indicator.
    """
    __tablename__ = "threat_horizon_indicators"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    indicator_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), default="RANSOMWARE_CAMPAIGN", nullable=False)
    trajectory_trend: Mapped[str] = mapped_column(String(20), default="SURGING", nullable=False)  # SURGING, STABLE, DECLINING
    observed_global_sightings: Mapped[int] = mapped_column(Integer, default=4890, nullable=False)

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
