"""
tests/unit/test_phase48_platform_service.py
===========================================
Unit tests for MLModelPlatformService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.ml_model_platform_service import MLModelPlatformService
from backend.app.models.ai_ml_model_platform import MLModelRegistryV2


@pytest.mark.asyncio
async def test_get_platform_summary():
    db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar.return_value = 5
    db.execute.return_value = mock_scalar

    summary = await MLModelPlatformService.get_platform_summary(db=db, tenant_id="tenant-ml-test")
    assert summary["platform_intelligence_score"] >= 95.0
    assert summary["platform_tier"] == "GLOBAL_AUTONOMOUS_AI_PLATFORM"
    assert "CatBoost-ThreatClassifier" in summary["champion_model"]
    assert summary["champion_accuracy"] == 0.9971
    assert summary["drift_monitoring_enabled"] is True
    assert summary["adversarial_defense_enabled"] is True


@pytest.mark.asyncio
async def test_register_model():
    db = AsyncMock()
    model = await MLModelPlatformService.register_model(
        db=db,
        tenant_id="tenant-ml-test",
        model_name="Custom-BERT-Classifier",
        model_version="v1.0.0",
        model_type="TRANSFORMER",
        model_family="THREAT_CLASSIFICATION",
        framework="pytorch",
        accuracy=0.9980,
        f1_score=0.9978,
        tags=["custom", "nlp"],
        hyperparameters={"epochs": 5}
    )
    assert model["model_name"] == "Custom-BERT-Classifier"
    assert model["model_version"] == "v1.0.0"
    assert model["accuracy"] == 0.9980
    assert model["status"] == "SHADOW"
    assert model["is_champion"] is False
    assert "custom" in model["tags"]


@pytest.mark.asyncio
async def test_get_champion_model_with_mock():
    db = AsyncMock()
    mock_champ = MLModelRegistryV2(
        id="champ-1",
        tenant_id="tenant-ml-test",
        model_name="CatBoost-ThreatClassifier",
        model_version="v3.2.1",
        model_type="GRADIENT_BOOSTING",
        model_family="THREAT_CLASSIFICATION",
        framework="catboost",
        accuracy=0.9971,
        f1_score=0.9968,
        roc_auc=0.9994,
        inference_p99_ms=3.2,
        status="ACTIVE",
        is_champion=True,
        tags_json=["champion", "production"]
    )
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_champ
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    champ = await MLModelPlatformService.get_champion_model(db=db, tenant_id="tenant-ml-test")
    assert champ is not None
    assert champ["model_name"] == "CatBoost-ThreatClassifier"
    assert champ["is_champion"] is True
    assert champ["roc_auc"] == 0.9994
