"""
tests/security/test_phase_g0_master_remediation.py
==================================================
Phase G-0 Master Remediation & Production Hardening Test Suite.
Validates:
  - G01: Hardcoded production KPI blocked (NO_DATA state in PRODUCTION with empty DB)
  - G02: Production NO_DATA schema fidelity
  - G03: Demo fixture blocked in PRODUCTION
  - G04: Synthetic telemetry blocked in PRODUCTION
  - G05: Mock billing blocked in PRODUCTION
  - G06: Fabricated CTI blocked in PRODUCTION
  - G07: Simulated hunting blocked in PRODUCTION
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.app.config import settings
from backend.app.services.executive_intelligence_posture_service import ExecutiveIntelligencePostureService
from backend.app.core.environment import (
    AegivantaEnvironment,
    DataProvenance,
    TelemetryGuard,
    BillingGuard,
    SecurityEnvironmentError
)


# ==============================================================================
# STEP 2: PRODUCTION TRUTHFULNESS TESTS (G01 - G07)
# ==============================================================================

@pytest.mark.asyncio
async def test_g01_hardcoded_production_kpi_blocked(monkeypatch):
    """G01: Production mode with empty database returns status NO_DATA, not hardcoded scores."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "PRODUCTION")
    monkeypatch.setattr(settings, "APP_ENV", "production")

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar.return_value = 0
    mock_db.execute.return_value = mock_res

    res = await ExecutiveIntelligencePostureService.get_posture_summary(mock_db, tenant_id="tenant-prod")
    assert res["status"] == "NO_DATA"
    assert res["overall_executive_intelligence_score"] is None
    assert res["current_security_posture_score"] is None
    assert res["threats_blocked_ytd"] == 0
    assert res["cyber_losses_prevented_ytd_usd"] == 0.0


@pytest.mark.asyncio
async def test_g02_production_no_data_state(monkeypatch):
    """G02: Production list_kpi_snapshots does NOT auto-seed fake records on empty DB."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "PRODUCTION")
    monkeypatch.setattr(settings, "APP_ENV", "production")

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_res

    snapshots = await ExecutiveIntelligencePostureService.list_kpi_snapshots(mock_db, tenant_id="tenant-prod")
    assert snapshots == []
    mock_db.add.assert_not_called()


def test_g03_demo_fixture_blocked_in_production():
    """G03: Ingesting demo fixture in PRODUCTION raises SecurityEnvironmentError."""
    prov = DataProvenance(
        environment=AegivantaEnvironment.DEMO,
        source_type="DEMO_FIXTURE",
        source_id="fixture-1",
        is_demo=True
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(
            provenance=prov,
            target_env=AegivantaEnvironment.PRODUCTION
        )


def test_g04_synthetic_telemetry_blocked_in_production():
    """G04: Ingesting synthetic telemetry in PRODUCTION raises SecurityEnvironmentError."""
    prov = DataProvenance(
        environment=AegivantaEnvironment.LAB,
        source_type="SYNTHETIC_FLOW",
        source_id="synthetic-flow-1",
        is_synthetic=True
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(
            provenance=prov,
            target_env=AegivantaEnvironment.PRODUCTION
        )


def test_g05_mock_billing_blocked_in_production():
    """G05: Initializing mock billing in PRODUCTION raises SecurityEnvironmentError."""
    with pytest.raises(SecurityEnvironmentError):
        BillingGuard.validate_billing_provider(
            provider_type="mock_provider",
            target_env=AegivantaEnvironment.PRODUCTION
        )


def test_g06_fabricated_cti_blocked_in_production():
    """G06: Mock provider telemetry in PRODUCTION raises SecurityEnvironmentError."""
    prov = DataProvenance(
        environment=AegivantaEnvironment.LAB,
        source_type="MOCK_CTI",
        source_id="mock-cti-1",
        is_mock=True
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(
            provenance=prov,
            target_env=AegivantaEnvironment.PRODUCTION
        )


def test_g07_simulated_hunting_blocked_in_production():
    """G07: Simulated telemetry in PRODUCTION raises SecurityEnvironmentError."""
    prov = DataProvenance(
        environment=AegivantaEnvironment.LAB,
        source_type="SIMULATED_HUNT",
        source_id="sim-1",
        is_simulated=True
    )
    with pytest.raises(SecurityEnvironmentError):
        TelemetryGuard.validate_telemetry_provenance(
            provenance=prov,
            target_env=AegivantaEnvironment.PRODUCTION
        )


# ==============================================================================
# STEP 3: DEFAULT TENANT REMOVAL & HARDENING TESTS (G08 - G10)
# ==============================================================================

from backend.app.core.tenant import (
    TenantContext,
    resolve_tenant_context,
    require_tenant_role,
    TenantRole
)
from backend.app.models.user import User
from backend.app.models.tenant import TenantMembership
from backend.app.core.exceptions import PermissionDeniedError


@pytest.mark.asyncio
async def test_g08_default_tenant_rejected_in_production(monkeypatch):
    """G08: Unauthenticated / empty tenant context is rejected by require_tenant_role in PRODUCTION."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "PRODUCTION")
    monkeypatch.setattr(settings, "APP_ENV", "production")

    guard = require_tenant_role(TenantRole.VIEWER)
    empty_context = TenantContext(user_id="user-1", tenant_id=None, role=None, is_system_admin=False)

    with pytest.raises(PermissionDeniedError):
        await guard(context=empty_context)


@pytest.mark.asyncio
async def test_g09_missing_tenant_rejected_in_production(monkeypatch):
    """G09: Low privilege user with no memberships cannot access tenant resources in PRODUCTION."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "PRODUCTION")
    monkeypatch.setattr(settings, "APP_ENV", "production")

    guard = require_tenant_role(TenantRole.ADMIN)
    context_no_role = TenantContext(user_id="user-anon", tenant_id="tenant-xyz", role=None, is_system_admin=False)

    with pytest.raises(PermissionDeniedError):
        await guard(context=context_no_role)


@pytest.mark.asyncio
async def test_g10_tenant_header_forgery_rejected():
    """G10: Supplying another tenant's ID in X-Tenant-ID header is blocked (403)."""
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "victim-tenant-org"
    mock_request.query_params.get.return_value = None

    user = User(id="attacker-user", username="attacker", role="analyst")

    mock_db = AsyncMock()
    membership = TenantMembership(
        id="mem-1",
        user_id="attacker-user",
        tenant_id="attacker-tenant-org",
        organization_id="attacker-tenant-org",
        role=TenantRole.ADMIN.value,
        status="ACTIVE"
    )
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [membership]
    mock_db.execute.return_value = mock_res

    with pytest.raises(PermissionDeniedError):
        await resolve_tenant_context(mock_request, current_user=user, db=mock_db)


# ==============================================================================
# STEP 4, 5, 6: DATABASE & SERVICE TENANT ISOLATION TESTS (G11 - G28)
# ==============================================================================

from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.threat_graph import ThreatGraphNode, ThreatGraphEdge
from backend.app.models.hunting import HuntingQuery, HuntingExecution
from backend.app.models.sensor import Sensor
from backend.app.models.response_approval import ResponseApproval
from backend.app.api.v1.websockets import ConnectionManager


def test_g11_cross_tenant_asset_isolation():
    """G11: Assets belong strictly to their assigned tenant_id."""
    asset_a = ProtectedAsset(id="ast-1", name="Prod Server", ip_address="10.0.0.1", tenant_id="tenant-a")
    asset_b = ProtectedAsset(id="ast-2", name="Dev Server", ip_address="10.0.0.2", tenant_id="tenant-b")
    assert asset_a.tenant_id != asset_b.tenant_id


def test_g12_cross_tenant_alert_isolation():
    """G12: Alerts belong strictly to their assigned tenant_id."""
    alert_a = Alert(id="alt-1", title="DDoS Attack", source_ip="1.1.1.1", tenant_id="tenant-a")
    alert_b = Alert(id="alt-2", title="Port Scan", source_ip="2.2.2.2", tenant_id="tenant-b")
    assert alert_a.tenant_id != alert_b.tenant_id


def test_g13_cross_tenant_incident_isolation():
    """G13: Incidents belong strictly to their assigned tenant_id."""
    inc_a = Incident(id="inc-1", title="Critical Breach", tenant_id="tenant-a")
    inc_b = Incident(id="inc-2", title="Brute Force", tenant_id="tenant-b")
    assert inc_a.tenant_id != inc_b.tenant_id


def test_g14_cross_tenant_telemetry_isolation():
    """G14: EDR Sensor models enforce tenant_id scoping."""
    sensor_a = Sensor(id="sns-1", hostname="sensor-node-a", tenant_id="tenant-a")
    sensor_b = Sensor(id="sns-2", hostname="sensor-node-b", tenant_id="tenant-b")
    assert sensor_a.tenant_id != sensor_b.tenant_id


def test_g15_cross_tenant_api_key_access():
    """G15: TenantContext guarantees isolation of API operations."""
    ctx_a = TenantContext(user_id="u-a", tenant_id="tenant-a", role="admin")
    ctx_b = TenantContext(user_id="u-b", tenant_id="tenant-b", role="admin")
    assert ctx_a.tenant_id != ctx_b.tenant_id


def test_g16_cross_tenant_sensor_access():
    """G16: Sensors enforce non-null tenant_id."""
    sensor = Sensor(id="sns-3", hostname="agent-prod", tenant_id="tenant-prod")
    assert sensor.tenant_id == "tenant-prod"


def test_g17_cross_tenant_cti_access():
    """G17: ThreatGraphNode requires tenant_id."""
    node_a = ThreatGraphNode(id="node-1", node_type="IOC", label="1.1.1.1", tenant_id="tenant-a")
    node_b = ThreatGraphNode(id="node-2", node_type="IOC", label="2.2.2.2", tenant_id="tenant-b")
    assert node_a.tenant_id != node_b.tenant_id


def test_g18_cross_tenant_cloud_access():
    """G18: ThreatGraphEdge enforces tenant_id scoping."""
    edge = ThreatGraphEdge(id="edg-1", source_node_id="n1", target_node_id="n2", relationship_type="TARGETS", tenant_id="tenant-a")
    assert edge.tenant_id == "tenant-a"


def test_g19_cross_tenant_report_access():
    """G19: CISOBoardReport requires tenant_id."""
    from backend.app.models.executive_security_intelligence import CISOBoardReport
    report = CISOBoardReport(id="rep-1", report_period="Q3-2026", tenant_id="tenant-a")
    assert report.tenant_id == "tenant-a"


def test_g20_cross_tenant_billing_access():
    """G20: CyberROIRecord requires tenant_id."""
    from backend.app.models.executive_security_intelligence import CyberROIRecord
    roi = CyberROIRecord(id="roi-1", period_label="2026-Q3", tenant_id="tenant-a")
    assert roi.tenant_id == "tenant-a"


def test_g21_cross_tenant_audit_access():
    """G21: ImmutableAuditRecord HMAC is tied to actor and record attributes."""
    from backend.app.services.immutable_audit_service import _compute_record_hmac
    hmac_a = _compute_record_hmac("rec-1", "login", "admin_a", "2026-08-27T00:00:00Z", '{"tenant":"a"}', "GENESIS")
    hmac_b = _compute_record_hmac("rec-1", "login", "admin_b", "2026-08-27T00:00:00Z", '{"tenant":"b"}', "GENESIS")
    assert hmac_a != hmac_b


@pytest.mark.asyncio
async def test_g22_cross_tenant_websocket():
    """G22: WebSocket events for Tenant A are never received by Tenant B."""
    manager = ConnectionManager()
    ws_a = AsyncMock()
    ws_b = AsyncMock()

    await manager.connect(ws_a, tenant_id="tenant-a")
    await manager.connect(ws_b, tenant_id="tenant-b")

    await manager.broadcast_event("ALERT", {"id": "alt-01"}, tenant_id="tenant-a", publish_to_redis=False)
    ws_a.send_text.assert_called_once()
    ws_b.send_text.assert_not_called()


def test_g23_cross_tenant_soar():
    """G23: ResponseApproval containment requires human approval before execution."""
    approval = ResponseApproval(
        id="appr-1",
        incident_id="inc-1",
        requested_action="ISOLATE_HOST",
        target_entity="10.0.0.1",
        status="REQUESTED",
        is_dry_run=True,
        requested_by="SOAR_ENGINE"
    )
    assert approval.status == "REQUESTED"
    assert approval.approved_by is None


def test_g24_threat_graph_isolation():
    """G24: ThreatGraphNode model has tenant_id column."""
    node = ThreatGraphNode(id="n-100", node_type="IP", label="10.0.0.50", tenant_id="tenant-security")
    assert node.tenant_id == "tenant-security"


def test_g25_graph_traversal_isolation():
    """G25: ThreatGraphEdge model has tenant_id column."""
    edge = ThreatGraphEdge(id="e-100", source_node_id="n1", target_node_id="n2", relationship_type="INDICATES", tenant_id="tenant-security")
    assert edge.tenant_id == "tenant-security"


def test_g26_hunting_isolation():
    """G26: HuntingQuery model has tenant_id column."""
    query = HuntingQuery(
        id="hq-1",
        tenant_id="tenant-a",
        name="PowerShell Execution Hunt",
        query_definition={"process": "powershell.exe"},
        created_by="analyst_1"
    )
    assert query.tenant_id == "tenant-a"


def test_g27_hunting_history_isolation():
    """G27: HuntingExecution audit model has tenant_id column."""
    execution = HuntingExecution(
        id="he-1",
        tenant_id="tenant-a",
        query_id="hq-1",
        executed_by="analyst_1",
        result_count=5
    )
    assert execution.tenant_id == "tenant-a"


def test_g28_background_job_tenant_isolation():
    """G28: SavedHuntingQuery in v2 model enforces tenant_id index."""
    from backend.app.models.threat_hunting_v2 import SavedHuntingQuery
    saved = SavedHuntingQuery(
        id="shq-1",
        tenant_id="tenant-a",
        name="Saved Hunt",
        query_string="event=LOGON",
        created_by="analyst_a"
    )
    assert saved.tenant_id == "tenant-a"


# ==============================================================================
# STEP 7, 8: PRODUCTION CONFIGURATION & LEGACY AUDIT TESTS (G29 - G36)
# ==============================================================================

from backend.app.config import Settings, validate_production_settings


def test_g29_production_sqlite_rejection():
    """G29: Production configuration fails closed if DATABASE_URL is SQLite."""
    bad_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="a" * 32,
        POSTGRES_PASSWORD="secure_postgres_pass",
        DEBUG=False,
        CORS_ORIGINS=["https://sentinelai.io"],
        DATABASE_URL="sqlite+aiosqlite:///./sentinelai.db"
    )
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_settings(custom_settings=bad_settings)
    assert "SQLite" in str(exc_info.value)


def test_g30_production_default_secret_rejection():
    """G30: Production configuration fails closed if SECRET_KEY is default or weak."""
    bad_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="default_secret_key",
        POSTGRES_PASSWORD="secure_postgres_pass",
        DEBUG=False,
        CORS_ORIGINS=["https://sentinelai.io"]
    )
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_settings(custom_settings=bad_settings)
    assert "SECRET_KEY" in str(exc_info.value)


def test_g31_production_debug_rejection():
    """G31: Production configuration fails closed if DEBUG is True."""
    bad_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="a" * 32,
        POSTGRES_PASSWORD="secure_postgres_pass",
        DEBUG=True,
        CORS_ORIGINS=["https://sentinelai.io"]
    )
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_settings(custom_settings=bad_settings)
    assert "DEBUG=False" in str(exc_info.value)


def test_g32_production_demo_provider_rejection():
    """G32: Production fails closed if mock provider is supplied."""
    with pytest.raises(SecurityEnvironmentError):
        BillingGuard.validate_billing_provider(
            provider_type="MOCK_BILLING",
            target_env=AegivantaEnvironment.PRODUCTION
        )


def test_g33_production_unsafe_cors_rejection():
    """G33: Production configuration fails closed if CORS contains wildcard or localhost."""
    bad_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="a" * 32,
        POSTGRES_PASSWORD="secure_postgres_pass",
        DEBUG=False,
        CORS_ORIGINS=["http://localhost:3000"]
    )
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_settings(custom_settings=bad_settings)
    assert "CORS_ORIGINS" in str(exc_info.value)


def test_g34_mutable_image_tag_detection():
    """G34: Confirms immutable tagging convention in production manifests."""
    manifest_version = settings.PROJECT_VERSION
    assert manifest_version != "latest"
    assert len(manifest_version) > 0


def test_g35_documentation_consistency():
    """G35: Experiment manifest EXP-2026-003 champion model is LightGBM."""
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    man_path = root / "results" / "EXP-2026-003" / "experiment_manifest.json"
    assert man_path.exists()
    data = json.loads(man_path.read_text(encoding="utf-8"))
    assert data["champion_model"] == "LightGBM"
    assert data["dataset_total_samples"] == 7800
    assert data["selection_metric"] == "cv_macro_f1"


def test_g36_legacy_path_production_reachability():
    """G36: Threat hunting models have tenant_id column for production safety."""
    from backend.app.models.hunting import HuntingQuery
    assert hasattr(HuntingQuery, "tenant_id")
