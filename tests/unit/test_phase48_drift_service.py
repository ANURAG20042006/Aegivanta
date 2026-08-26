"""
tests/unit/test_phase48_drift_service.py
========================================
Unit tests for DriftMonitoringService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.drift_monitoring_service import DriftMonitoringService
from backend.app.models.ai_ml_model_platform import MLModelDriftRecord


@pytest.mark.asyncio
async def test_get_drift_summary():
    db = AsyncMock()
    mock_drift = MLModelDriftRecord(
        id="drift-1",
        tenant_id="tenant-ml-test",
        model_id="cat-001",
        model_name="CatBoost-ThreatClassifier",
        model_version="v3.2.1",
        data_drift_score=0.012,
        concept_drift_score=0.008,
        prediction_drift_score=0.015,
        drift_severity="NONE",
        drift_method="PSI",
        feature_drift_breakdown_json={"feature_1": 0.01},
        alert_triggered=False,
        auto_retrain_triggered=False
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_drift]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    summary = await DriftMonitoringService.get_drift_summary(db=db, tenant_id="tenant-ml-test")
    assert summary["drift_monitoring_score"] >= 90.0
    assert summary["models_monitored"] == 1
    assert summary["drift_method_primary"] == "PSI"
    assert summary["drift_threshold_alert"] == 0.05
    assert summary["drift_threshold_retrain"] == 0.07



@pytest.mark.asyncio
async def test_list_drift_records_with_mock():
    db = AsyncMock()
    mock_drift = MLModelDriftRecord(
        id="drift-1",
        tenant_id="tenant-ml-test",
        model_id="cat-001",
        model_name="CatBoost-ThreatClassifier",
        model_version="v3.2.1",
        data_drift_score=0.012,
        concept_drift_score=0.008,
        prediction_drift_score=0.015,
        drift_severity="NONE",
        drift_method="PSI",
        feature_drift_breakdown_json={"feature_1": 0.01},
        alert_triggered=False,
        auto_retrain_triggered=False
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_drift]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    records = await DriftMonitoringService.list_drift_records(db=db, tenant_id="tenant-ml-test")
    assert isinstance(records, list)
    assert len(records) >= 1
    assert records[0]["model_name"] == "CatBoost-ThreatClassifier"
    assert records[0]["drift_severity"] == "NONE"
    assert records[0]["drift_method"] == "PSI"
