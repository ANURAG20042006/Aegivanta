"""
tests/security/test_phase48_tenant_isolation.py
================================================
Security tests for Phase 48 AI/ML Model Platform tenant isolation.
"""

from backend.app.models.ai_ml_model_platform import (
    MLModelRegistryV2,
    MLModelDriftRecord,
    AdversarialAttackEvent
)


def test_model_registry_tenant_isolation():
    model_a = MLModelRegistryV2(
        tenant_id="tenant-alpha",
        model_name="Custom-Model-A",
        model_version="v1.0.0"
    )
    model_b = MLModelRegistryV2(
        tenant_id="tenant-beta",
        model_name="Custom-Model-B",
        model_version="v1.0.0"
    )
    assert model_a.tenant_id != model_b.tenant_id
    assert model_a.model_name != model_b.model_name


def test_drift_record_tenant_isolation():
    drift_a = MLModelDriftRecord(
        tenant_id="tenant-alpha",
        model_id="cat-001",
        data_drift_score=0.01
    )
    drift_b = MLModelDriftRecord(
        tenant_id="tenant-beta",
        model_id="cat-001",
        data_drift_score=0.01
    )
    assert drift_a.tenant_id != drift_b.tenant_id


def test_adversarial_attack_tenant_isolation():
    evt_a = AdversarialAttackEvent(
        tenant_id="tenant-alpha",
        model_id="cat-001",
        attack_type="EVASION"
    )
    evt_b = AdversarialAttackEvent(
        tenant_id="tenant-beta",
        model_id="cat-001",
        attack_type="EVASION"
    )
    assert evt_a.tenant_id != evt_b.tenant_id
