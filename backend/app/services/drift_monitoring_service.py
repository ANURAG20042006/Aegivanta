"""
backend/app/services/drift_monitoring_service.py
=================================================
Phase 48 — ML Model Drift Monitoring service.
Computes, stores, and evaluates statistical drift records for all production models.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.ai_ml_model_platform import MLModelDriftRecord


# Drift seed data — baseline for all 5 production models
_DRIFT_SEEDS = [
    {
        "model_id": "cat-001",
        "model_name": "CatBoost-ThreatClassifier",
        "model_version": "v3.2.1",
        "data_drift_score": 0.012,
        "concept_drift_score": 0.008,
        "prediction_drift_score": 0.015,
        "drift_severity": "NONE",
        "drift_method": "PSI",
        "alert_triggered": False,
        "auto_retrain_triggered": False,
        "features": {"threat_score": 0.010, "source_port": 0.008, "bytes_transferred": 0.014},
    },
    {
        "model_id": "xgb-001",
        "model_name": "XGBoost-AnomalyDetector",
        "model_version": "v2.8.0",
        "data_drift_score": 0.041,
        "concept_drift_score": 0.028,
        "prediction_drift_score": 0.053,
        "drift_severity": "LOW",
        "drift_method": "KS_TEST",
        "alert_triggered": True,
        "auto_retrain_triggered": False,
        "features": {"session_duration": 0.038, "login_failures": 0.045, "geo_distance": 0.051},
    },
    {
        "model_id": "gnn-001",
        "model_name": "PyTorch-GNN-LateralMovement",
        "model_version": "v1.5.0",
        "data_drift_score": 0.021,
        "concept_drift_score": 0.014,
        "prediction_drift_score": 0.027,
        "drift_severity": "NONE",
        "drift_method": "EVIDENTLY",
        "alert_triggered": False,
        "auto_retrain_triggered": False,
        "features": {"graph_degree": 0.018, "hop_count": 0.023, "service_edge_weight": 0.019},
    },
    {
        "model_id": "trans-001",
        "model_name": "Transformer-NLP-PhishingDetector",
        "model_version": "v2.1.3",
        "data_drift_score": 0.061,
        "concept_drift_score": 0.042,
        "prediction_drift_score": 0.079,
        "drift_severity": "MEDIUM",
        "drift_method": "PSI",
        "alert_triggered": True,
        "auto_retrain_triggered": True,
        "features": {"token_distribution": 0.058, "domain_reputation": 0.072, "link_density": 0.060},
    },
    {
        "model_id": "iso-001",
        "model_name": "IsolationForest-ExfiltrationDetector",
        "model_version": "v1.9.2",
        "data_drift_score": 0.018,
        "concept_drift_score": 0.011,
        "prediction_drift_score": 0.022,
        "drift_severity": "NONE",
        "drift_method": "KS_TEST",
        "alert_triggered": False,
        "auto_retrain_triggered": False,
        "features": {"bytes_out": 0.015, "unique_destinations": 0.020, "protocol_ratio": 0.011},
    },
]


from backend.app.config import settings


class DriftMonitoringService:

    @classmethod
    async def list_drift_records(
        cls,
        db: AsyncSession,
        tenant_id: str = "default-tenant",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists all drift monitoring records for all models."""
        is_production = (
            getattr(settings, "OPERATING_MODE", "").upper() == "PRODUCTION" or
            getattr(settings, "APP_ENV", "").lower() == "production" or
            getattr(settings, "AEGIVANTA_ENVIRONMENT", "").upper() == "PRODUCTION"
        )
        result = await db.execute(
            select(MLModelDriftRecord)
            .where(MLModelDriftRecord.tenant_id == tenant_id)
            .order_by(MLModelDriftRecord.detected_at.desc())
            .limit(limit)
        )
        records = result.scalars().all()

        if not records and not is_production:
            await cls._seed_defaults(db, tenant_id)
            result2 = await db.execute(
                select(MLModelDriftRecord)
                .where(MLModelDriftRecord.tenant_id == tenant_id)
                .order_by(MLModelDriftRecord.detected_at.desc())
                .limit(limit)
            )
            records = result2.scalars().all()

        return [cls._serialize(r) for r in records]

    @classmethod
    async def get_drift_summary(
        cls,
        db: AsyncSession,
        tenant_id: str = "default-tenant"
    ) -> Dict[str, Any]:
        """Returns dynamic drift monitoring platform summary derived from active database records."""
        is_production = (
            getattr(settings, "OPERATING_MODE", "").upper() == "PRODUCTION" or
            getattr(settings, "APP_ENV", "").lower() == "production" or
            getattr(settings, "AEGIVANTA_ENVIRONMENT", "").upper() == "PRODUCTION"
        )
        result = await db.execute(
            select(MLModelDriftRecord)
            .where(MLModelDriftRecord.tenant_id == tenant_id)
            .order_by(MLModelDriftRecord.detected_at.desc())
        )
        records = result.scalars().all()

        if not records and is_production:
            return {
                "status": "NO_DATA",
                "drift_monitoring_score": None,
                "models_monitored": 0,
                "models_with_no_drift": 0,
                "models_with_low_drift": 0,
                "models_with_medium_drift": 0,
                "models_with_high_drift": 0,
                "auto_retrain_triggered_this_week": 0,
                "drift_method_primary": "PSI",
                "drift_threshold_alert": 0.05,
                "drift_threshold_retrain": 0.07,
                "evaluated_at": datetime.now(timezone.utc).isoformat()
            }

        if not records:
            # In demo/lab mode, seed baseline if empty
            await cls._seed_defaults(db, tenant_id)
            result2 = await db.execute(
                select(MLModelDriftRecord)
                .where(MLModelDriftRecord.tenant_id == tenant_id)
            )
            records = result2.scalars().all()

        unique_models = set(r.model_id for r in records)
        no_drift = sum(1 for r in records if r.drift_severity == "NONE")
        low_drift = sum(1 for r in records if r.drift_severity == "LOW")
        med_drift = sum(1 for r in records if r.drift_severity == "MEDIUM")
        high_drift = sum(1 for r in records if r.drift_severity in ["HIGH", "CRITICAL"])
        retrains = sum(1 for r in records if r.auto_retrain_triggered)

        avg_drift = sum(r.data_drift_score for r in records) / max(len(records), 1)
        score = round(max(0.0, 100.0 - (avg_drift * 100.0)), 1)

        return {
            "drift_monitoring_score": score,
            "models_monitored": len(unique_models) or len(records),
            "models_with_no_drift": no_drift,
            "models_with_low_drift": low_drift,
            "models_with_medium_drift": med_drift,
            "models_with_high_drift": high_drift,
            "auto_retrain_triggered_this_week": retrains,
            "drift_method_primary": "PSI",
            "drift_threshold_alert": 0.05,
            "drift_threshold_retrain": 0.07,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    async def _seed_defaults(cls, db: AsyncSession, tenant_id: str) -> None:
        for seed in _DRIFT_SEEDS:
            db.add(MLModelDriftRecord(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                model_id=seed["model_id"],
                model_name=seed["model_name"],
                model_version=seed["model_version"],
                data_drift_score=seed["data_drift_score"],
                concept_drift_score=seed["concept_drift_score"],
                prediction_drift_score=seed["prediction_drift_score"],
                drift_severity=seed["drift_severity"],
                drift_method=seed["drift_method"],
                feature_drift_breakdown_json=seed.get("features", {}),
                alert_triggered=seed["alert_triggered"],
                auto_retrain_triggered=seed["auto_retrain_triggered"],
                detected_at=datetime.now(timezone.utc)
            ))
        await db.flush()


    @staticmethod
    def _serialize(r: MLModelDriftRecord) -> Dict[str, Any]:
        return {
            "id": r.id,
            "model_id": r.model_id,
            "model_name": r.model_name,
            "model_version": r.model_version,
            "data_drift_score": r.data_drift_score,
            "concept_drift_score": r.concept_drift_score,
            "prediction_drift_score": r.prediction_drift_score,
            "drift_severity": r.drift_severity,
            "drift_method": r.drift_method,
            "feature_drift_breakdown": r.feature_drift_breakdown_json,
            "alert_triggered": r.alert_triggered,
            "auto_retrain_triggered": r.auto_retrain_triggered,
            "remediation_action": r.remediation_action,
            "detected_at": r.detected_at.isoformat() if r.detected_at else None
        }
