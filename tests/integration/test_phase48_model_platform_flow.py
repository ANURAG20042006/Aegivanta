"""
tests/integration/test_phase48_model_platform_flow.py
=====================================================
Integration tests for the complete AI/ML Model Platform flow:
platform scorecard -> model registration -> drift monitoring -> adversarial defense simulation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.ml_model_platform_service import MLModelPlatformService
from backend.app.services.drift_monitoring_service import DriftMonitoringService
from backend.app.services.adversarial_defense_service import AdversarialDefenseService


@pytest.mark.asyncio
async def test_full_ml_model_platform_flow():
    db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar.return_value = 5
    db.execute.return_value = mock_scalar

    # 1. Check Platform Posture Scorecard
    summary = await MLModelPlatformService.get_platform_summary(
        db=db, tenant_id="tenant-integration-ml"
    )
    assert summary["platform_intelligence_score"] >= 95.0
    assert summary["platform_tier"] == "GLOBAL_AUTONOMOUS_AI_PLATFORM"

    # 2. Register New Candidate Model Version
    new_model = await MLModelPlatformService.register_model(
        db=db,
        tenant_id="tenant-integration-ml",
        model_name="CatBoost-ThreatClassifier",
        model_version="v3.3.0-rc1",
        model_type="GRADIENT_BOOSTING",
        model_family="THREAT_CLASSIFICATION",
        framework="catboost",
        accuracy=0.9978,
        f1_score=0.9975,
        roc_auc=0.9997,
        tags=["candidate", "shadow"]
    )
    assert new_model["model_version"] == "v3.3.0-rc1"
    assert new_model["status"] == "SHADOW"

    # 3. Check Drift Posture
    drift_sum = await DriftMonitoringService.get_drift_summary(
        db=db, tenant_id="tenant-integration-ml"
    )
    assert drift_sum["drift_monitoring_score"] >= 90.0
    assert drift_sum["models_monitored"] >= 0

    # 4. Trigger Adversarial Defense Simulation
    defense_result = await AdversarialDefenseService.simulate_defense(
        db=db,
        tenant_id="tenant-integration-ml",
        model_id="cat-001",
        attack_type="EVASION",
        attack_payload={"feature": "bytes_transferred", "perturbation": 0.05}
    )
    assert defense_result["outcome"] == "ATTACK_BLOCKED"
    assert defense_result["blocked"] is True

    # 5. Check Adversarial Defense Summary
    adv_sum = await AdversarialDefenseService.get_defense_summary(
        db=db, tenant_id="tenant-integration-ml"
    )
    assert adv_sum["block_rate"] >= 0.0
    assert adv_sum["total_attacks_blocked_30d"] >= 0
