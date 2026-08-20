"""
tests/unit/test_phase10_adaptive_detection.py
=============================================
Unit tests for Analyst Feedback Loops, Drift Measurement, and Challenger Model Promotion.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.adaptive_feedback_service import AdaptiveFeedbackService
from backend.app.models.feedback import DetectionFeedback
from backend.app.models.model_registry import ModelRegistry


@pytest.mark.asyncio
async def test_compute_model_drift():
    """Validates calculation of accuracy ratios and drift alert trigger."""
    db = AsyncMock()
    # 80 True Positives, 20 False Positives -> 80% accuracy -> 0.20 drift score (no drift)
    fbs = [
        DetectionFeedback(actual_verdict="TRUE_POSITIVE", predicted_attack_type="DDoS") for _ in range(80)
    ] + [
        DetectionFeedback(actual_verdict="FALSE_POSITIVE", predicted_attack_type="Benign") for _ in range(20)
    ]
    res = MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=fbs))))
    db.execute = AsyncMock(return_value=res)

    drift_report = await AdaptiveFeedbackService.compute_model_drift(db, "CatBoost")

    assert drift_report["total_feedback_samples"] == 100
    assert drift_report["true_positives"] == 80
    assert drift_report["accuracy_ratio"] == 0.8
    assert drift_report["drift_detected"] is False


@pytest.mark.asyncio
async def test_promote_challenger_to_champion():
    """Validates safe promotion of candidate challenger model to active champion."""
    db = AsyncMock()
    challenger = ModelRegistry(id="mod-challenger", model_name="CatBoost-v2", status="CANDIDATE")
    existing_champion = ModelRegistry(id="mod-champ", model_name="CatBoost-v1", status="ACTIVE")

    res_challenger = MagicMock(scalar_one_or_none=MagicMock(return_value=challenger))
    res_champion = MagicMock(scalar_one_or_none=MagicMock(return_value=existing_champion))

    db.execute = AsyncMock(side_effect=[res_challenger, res_champion])
    db.flush = AsyncMock()

    result = await AdaptiveFeedbackService.promote_challenger_to_champion(db, "mod-challenger")

    assert result["status"] == "SUCCESS"
    assert challenger.status == "ACTIVE"
    assert existing_champion.status == "PREVIOUS_CHAMPION"
