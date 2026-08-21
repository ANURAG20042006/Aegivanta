"""
tests/unit/test_phase48_models.py
=================================
Unit tests for Phase 48 AI/ML Model Platform models.
"""

from backend.app.models.ai_ml_model_platform import (
    MLModelRegistryV2,
    MLModelDriftRecord,
    AdversarialAttackEvent
)


def test_ml_model_registry_v2_model():
    model = MLModelRegistryV2(
        tenant_id="tenant-ml-1",
        model_name="CatBoost-ThreatClassifier",
        model_version="v3.2.1",
        model_type="GRADIENT_BOOSTING",
        model_family="THREAT_CLASSIFICATION",
        framework="catboost",
        accuracy=0.9971,
        f1_score=0.9968,
        precision_score=0.9965,
        recall_score=0.9972,
        roc_auc=0.9994,
        inference_p99_ms=3.2,
        status="ACTIVE",
        is_champion=True,
        tags_json=["champion", "threat-detection"],
        hyperparameters_json={"depth": 6, "iterations": 1000}
    )
    assert model.model_name == "CatBoost-ThreatClassifier"
    assert model.model_version == "v3.2.1"
    assert model.accuracy == 0.9971
    assert model.is_champion is True
    assert model.status == "ACTIVE"
    assert "champion" in model.tags_json


def test_ml_model_drift_record_model():
    drift = MLModelDriftRecord(
        tenant_id="tenant-ml-1",
        model_id="cat-001",
        model_name="CatBoost-ThreatClassifier",
        model_version="v3.2.1",
        data_drift_score=0.012,
        concept_drift_score=0.008,
        prediction_drift_score=0.015,
        drift_severity="NONE",
        drift_method="PSI",
        feature_drift_breakdown_json={"threat_score": 0.010},
        alert_triggered=False,
        auto_retrain_triggered=False
    )
    assert drift.model_id == "cat-001"
    assert drift.drift_severity == "NONE"
    assert drift.data_drift_score == 0.012
    assert drift.drift_method == "PSI"
    assert drift.alert_triggered is False


def test_adversarial_attack_event_model():
    event = AdversarialAttackEvent(
        tenant_id="tenant-ml-1",
        model_id="cat-001",
        model_name="CatBoost-ThreatClassifier",
        attack_type="EVASION",
        attack_severity="HIGH",
        attack_vector_json={"technique": "feature_perturbation"},
        confidence_score=0.96,
        defense_mechanism="ADVERSARIAL_INPUT_DETECTION",
        blocked=True,
        defense_latency_ms=1.1
    )
    assert event.attack_type == "EVASION"
    assert event.attack_severity == "HIGH"
    assert event.blocked is True
    assert event.confidence_score == 0.96
    assert event.defense_latency_ms == 1.1
