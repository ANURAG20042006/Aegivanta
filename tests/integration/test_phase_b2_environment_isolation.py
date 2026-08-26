"""
tests/integration/test_phase_b2_environment_isolation.py
========================================================
Phase B2 Environment Separation, Fail-Closed Guards, and Anti-Fallback Test Suite.
"""

import os
import pytest
import hashlib
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.app.core.environment import (
    AegivantaEnvironment,
    DataProvenance,
    SecurityEnvironmentError,
    ProductionConfigurationError,
    TelemetryGuard,
    BillingGuard,
    ThreatIntelGuard,
    MLArtifactGuard,
    DatabaseGuard,
    get_authoritative_environment,
    record_security_violation,
    SECURITY_AUDIT_TRAIL
)
from backend.app.config import Settings, validate_production_settings


# ==============================================================================
# 1. NEGATIVE TESTS (TEST 01 - TEST 16)
# ==============================================================================

def test_01_production_synthetic_telemetry_rejected():
    """TEST 01: PRODUCTION + synthetic telemetry -> REJECT"""
    prov = DataProvenance(
        environment=AegivantaEnvironment.PRODUCTION,
        source_type="SYNTHETIC_GENERATOR",
        source_id="cicids2017_gen",
        is_synthetic=True,
        is_production=False
    )
    with pytest.raises(SecurityEnvironmentError) as exc_info:
        TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION)
    assert "synthetic" in str(exc_info.value).lower()


def test_02_production_demo_telemetry_rejected():
    """TEST 02: PRODUCTION + demo telemetry -> REJECT"""
    prov = DataProvenance(
        environment=AegivantaEnvironment.DEMO,
        source_type="DEMO_FIXTURE",
        source_id="demo_sensor_01",
        is_demo=True,
        is_production=False
    )
    with pytest.raises(SecurityEnvironmentError) as exc_info:
        TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION)
    assert "demo" in str(exc_info.value).lower() or "rejected" in str(exc_info.value).lower()


def test_03_production_mock_telemetry_rejected():
    """TEST 03: PRODUCTION + mock telemetry -> REJECT"""
    prov = DataProvenance(
        environment=AegivantaEnvironment.PRODUCTION,
        source_type="MOCK_EDR",
        source_id="mock_sensor_99",
        is_mock=True,
        is_production=False
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION)


def test_04_production_mock_billing_rejected():
    """TEST 04: PRODUCTION + mock billing -> REJECT"""
    with pytest.raises(ProductionConfigurationError) as exc_info:
        BillingGuard.validate_billing_provider("MockBillingProvider", AegivantaEnvironment.PRODUCTION)
    assert "mockbillingprovider" in str(exc_info.value).lower() or "mock" in str(exc_info.value).lower()


def test_05_production_fabricated_cti_rejected():
    """TEST 05: PRODUCTION + fabricated CTI -> REJECT"""
    fake_indicator = {
        "indicator": "192.0.2.1",
        "type": "ipv4",
        "is_synthetic": True,
        "source": "demo_seed"
    }
    with pytest.raises(SecurityEnvironmentError) as exc_info:
        ThreatIntelGuard.validate_indicator_provenance(fake_indicator, AegivantaEnvironment.PRODUCTION)
    assert "synthetic" in str(exc_info.value).lower()


def test_06_production_simulated_hunting_rejected():
    """TEST 06: PRODUCTION + simulated hunting (missing db) -> REJECT"""
    from backend.app.services.threat_hunting_service import ThreatHuntingService
    import asyncio

    # Set environment to PRODUCTION
    os.environ["AEGIVANTA_ENVIRONMENT"] = "PRODUCTION"
    try:
        with pytest.raises(SecurityEnvironmentError) as exc_info:
            asyncio.run(ThreatHuntingService.execute_dsl_query(entity="events", db=None))
        assert "production threat hunting requires an active database session" in str(exc_info.value).lower()
    finally:
        os.environ["AEGIVANTA_ENVIRONMENT"] = "DEMO"


def test_07_production_seeded_dashboard_metrics_rejected():
    """TEST 07: PRODUCTION + seeded dashboard metrics -> REJECT hardcoded fallbacks"""
    from backend.app.services.soc_dashboard_service import SOCDashboardService
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    # Mock empty DB
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = []
    mock_res.scalar.return_value = 0
    mock_db.execute.return_value = mock_res

    os.environ["AEGIVANTA_ENVIRONMENT"] = "PRODUCTION"
    try:
        metrics = asyncio.run(SOCDashboardService.get_overview_metrics(db=mock_db))
        # In production with 0 incidents, MTTD/MTTA must be 0.0 (never 1.2 or 3.5 fallback)
        assert metrics["mean_time_to_detect_minutes"] == 0.0
        assert metrics["mean_time_to_acknowledge_minutes"] == 0.0
        assert metrics["mean_time_to_respond_minutes"] == 0.0
    finally:
        os.environ["AEGIVANTA_ENVIRONMENT"] = "DEMO"


def test_08_production_demo_fixture_rejected():
    """TEST 08: PRODUCTION + demo fixture -> REJECT"""
    prov = DataProvenance(
        environment=AegivantaEnvironment.DEMO,
        source_type="FIXTURE_DATASET",
        source_id="sample_incidents.json",
        is_seeded=True
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION)


def test_09_production_missing_provider_fails_closed():
    """TEST 09: PRODUCTION + missing provider -> FAIL CLOSED"""
    with pytest.raises(ProductionConfigurationError):
        BillingGuard.validate_billing_provider("FAKE", AegivantaEnvironment.PRODUCTION)


def test_10_production_invalid_environment_fails_closed():
    """TEST 10: PRODUCTION + invalid environment -> FAIL CLOSED"""
    os.environ["AEGIVANTA_ENVIRONMENT"] = "SUPER_CUSTOM_INVALID_ENV"
    try:
        with pytest.raises(SecurityEnvironmentError):
            get_authoritative_environment()
    finally:
        os.environ["AEGIVANTA_ENVIRONMENT"] = "DEMO"


def test_11_production_missing_environment_fails_closed():
    """TEST 11: PRODUCTION + missing environment in production context -> FAIL CLOSED"""
    if "AEGIVANTA_ENVIRONMENT" in os.environ:
        del os.environ["AEGIVANTA_ENVIRONMENT"]
    if "OPERATING_MODE" in os.environ:
        del os.environ["OPERATING_MODE"]
    if "APP_ENV" in os.environ:
        del os.environ["APP_ENV"]

    os.environ["NODE_ENV"] = "production"
    try:
        with pytest.raises(ProductionConfigurationError):
            get_authoritative_environment()
    finally:
        if "NODE_ENV" in os.environ:
            del os.environ["NODE_ENV"]
        os.environ["AEGIVANTA_ENVIRONMENT"] = "DEMO"


def test_12_production_test_database_rejected():
    """TEST 12: PRODUCTION + test SQLite database -> REJECT"""
    with pytest.raises(ProductionConfigurationError) as exc_info:
        DatabaseGuard.validate_database_url("sqlite+aiosqlite:///./sentinelai.db", AegivantaEnvironment.PRODUCTION)
    assert "sqlite" in str(exc_info.value).lower()


def test_13_production_unapproved_ml_artifact_rejected(tmp_path):
    """TEST 13: PRODUCTION + unapproved ML artifact -> REJECT"""
    fake_art = tmp_path / "fake_model.joblib"
    fake_art.write_bytes(b"corrupted_or_unapproved_weights")

    with pytest.raises(SecurityEnvironmentError) as exc_info:
        MLArtifactGuard.verify_production_model_artifact(
            model_name="LightGBM",
            artifact_path=str(fake_art),
            expected_hash="expected_authentic_sha256_hash_1234567890abcdef",
            target_env=AegivantaEnvironment.PRODUCTION
        )
    assert "integrity check failed" in str(exc_info.value).lower()


def test_14_production_experimental_artifact_rejected(tmp_path):
    """TEST 14: PRODUCTION + missing artifact path -> REJECT"""
    missing_path = str(tmp_path / "non_existent_model.joblib")
    with pytest.raises(ProductionConfigurationError):
        MLArtifactGuard.verify_production_model_artifact(
            model_name="ExperimentalModel",
            artifact_path=missing_path,
            expected_hash="any_hash",
            target_env=AegivantaEnvironment.PRODUCTION
        )


def test_15_production_demo_websocket_source_rejected():
    """TEST 15: PRODUCTION + demo WebSocket data source -> REJECT"""
    prov = DataProvenance(
        environment=AegivantaEnvironment.DEMO,
        source_type="WEBSOCKET_DEMO_STREAM",
        source_id="ws_replay_node",
        is_demo=True
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION)


def test_16_production_simulated_soar_result_rejected():
    """TEST 16: PRODUCTION + simulated SOAR result -> REJECT"""
    prov = DataProvenance(
        environment=AegivantaEnvironment.PRODUCTION,
        source_type="SOAR_SIMULATION",
        source_id="playbook_dryrun_01",
        is_simulated=True
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION)


# ==============================================================================
# 2. POSITIVE TESTS (DEMO, LAB, PRODUCTION)
# ==============================================================================

def test_17_demo_mode_accepts_demo_data():
    """Positive: DEMO mode accepts demo fixtures, mock billing, and simulated telemetry."""
    prov = DataProvenance(
        environment=AegivantaEnvironment.DEMO,
        source_type="DEMO_FIXTURE",
        source_id="demo_01",
        is_demo=True,
        is_synthetic=True
    )
    assert TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.DEMO) is True
    assert BillingGuard.validate_billing_provider("MockBillingProvider", AegivantaEnvironment.DEMO) is True


def test_18_lab_mode_accepts_benchmark_telemetry():
    """Positive: LAB mode accepts research/benchmark datasets."""
    prov = DataProvenance(
        environment=AegivantaEnvironment.LAB,
        source_type="BENCHMARK_FLOW",
        source_id="ciciot2023_subset",
        is_synthetic=False,
        is_demo=False
    )
    assert TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.LAB) is True


def test_19_production_mode_accepts_verified_telemetry():
    """Positive: PRODUCTION mode accepts genuine, authenticated telemetry."""
    prov = DataProvenance(
        environment=AegivantaEnvironment.PRODUCTION,
        source_type="SENSOR_EDR",
        source_id="sensor_prod_linux_001",
        is_synthetic=False,
        is_mock=False,
        is_demo=False,
        is_production=True
    )
    assert TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION) is True
    assert DatabaseGuard.validate_database_url("postgresql+asyncpg://user:pass@db:5432/prod_db", AegivantaEnvironment.PRODUCTION) is True


# ==============================================================================
# 3. ANTI-FALLBACK & AUDIT TESTS
# ==============================================================================

def test_20_anti_fallback_guarantee():
    """Anti-Fallback: Real provider failure must NEVER silently downgrade to Mock/Demo in PRODUCTION."""
    with pytest.raises(ProductionConfigurationError):
        BillingGuard.validate_billing_provider("MOCK", AegivantaEnvironment.PRODUCTION)


def test_21_audit_trail_recorded_on_violation():
    """Audit Trail: Blocked violations generate structured security events."""
    initial_len = len(SECURITY_AUDIT_TRAIL)
    prov = DataProvenance(
        environment=AegivantaEnvironment.PRODUCTION,
        source_type="MOCK_STREAM",
        source_id="leak_test_node",
        is_mock=True
    )
    try:
        TelemetryGuard.validate_telemetry_provenance(prov, AegivantaEnvironment.PRODUCTION)
    except SecurityEnvironmentError:
        pass

    assert len(SECURITY_AUDIT_TRAIL) > initial_len
    latest = SECURITY_AUDIT_TRAIL[-1]
    assert latest["decision"] == "BLOCKED"
    assert latest["environment"] == "PRODUCTION"
    assert "leak_test_node" in latest["source"] or "MOCK_STREAM" in latest["source"]
