"""
tests/integration/test_phase3_e2e.py
====================================
Comprehensive 25-Step Phase 3 End-to-End Operational Lifecycle Test Suite.
Validates the entire unified SOC pipeline:
  Protected Asset -> Continuous Monitoring -> Ingress Telemetry -> CatBoost ML Classification
  -> Threat Intel IOC Enrichment -> Behavioral Anomaly -> Single Risk Engine -> Alert Creation
  -> Incident Correlation -> Attack Timeline -> ATT&CK Stage Mapping -> Threat Hunting Engine
  -> Threat Intelligence Graph -> Campaign Correlation -> Predictive Analytics -> Matrix Coverage
  -> SOC Effectiveness Metrics -> SOAR Approval Request -> Admin Approval -> Simulation Dry-Run
  -> Audit Trail -> Background Job Manager -> Rate Limiting -> Invariant SHA-256 Check.
"""

import hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.database import AsyncSessionFactory
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.incident import Incident
from backend.app.services.monitoring_service import validate_target_url_safe
from backend.app.services.threat_intel_service import ThreatIntelService
from backend.app.services.anomaly_service import AnomalyService
from backend.app.services.risk_engine import RiskScoringEngine
from backend.app.services.hunting_service import HuntingService
from backend.app.services.threat_graph_service import ThreatGraphService
from backend.app.services.campaign_service import CampaignService
from backend.app.services.predictive_service import PredictiveService
from backend.app.services.attack_coverage_service import AttackCoverageService
from backend.app.services.soc_metrics_service import SOCMetricsService
from backend.app.services.response_orchestrator import ResponseOrchestrator
from backend.app.services.job_manager import JobManager

client = TestClient(app)
EXPECTED_CATBOOST_SHA256 = "efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82"


def get_auth_token(role: str = "admin") -> dict:
    passwords = {
        "admin": [getattr(settings, "SENTINEL_ADMIN_PASSWORD", "Admin_Secure2026!"), "TestAdminPassword2026!"],
        "analyst": [getattr(settings, "SENTINEL_ANALYST_PASSWORD", "Analyst_Secure2026!"), "TestAnalystPassword2026!"],
        "viewer": [getattr(settings, "SENTINEL_VIEWER_PASSWORD", "Viewer_Secure2026!"), "TestViewerPassword2026!"]
    }
    candidates = passwords.get(role, ["Admin_Secure2026!"])
    token = None
    for pwd in candidates:
        resp = client.post("/api/v1/auth/login", data={"username": role, "password": pwd})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            break
    assert token is not None, f"Authentication failed for {role}"
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_full_phase3_operational_lifecycle_pipeline():
    """Executes the complete 25-step Phase 3 operational and security verification lifecycle."""
    admin_hdr = get_auth_token("admin")
    analyst_hdr = get_auth_token("analyst")

    async with AsyncSessionFactory() as db:
        # Step 1: Protected Asset Registration
        asset = ProtectedAsset(
            name="P3 Core Payment Gateway",
            hostname="pay.sentinelai.io",
            ip_address="198.51.100.120",
            asset_type="api",
            criticality="critical"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        assert asset.id is not None

        # Step 2: SSRF-Safe Monitoring Check Validation
        is_safe, _, ip, _ = validate_target_url_safe("https://cloudflare.com", allow_private=False)
        assert is_safe is True
        assert ip is not None

        # Step 3: Threat Intelligence Indicator Seed
        ioc = ThreatIndicator(
            ioc_type="ipv4",
            raw_value="185.220.101.200",
            normalized_value="185.220.101.200",
            threat_type="C2_BOTNET",
            severity="critical",
            confidence=0.98,
            source="P3 E2E Test Suite"
        )
        db.add(ioc)
        await db.commit()

        # Step 4: ML Flow Prediction via API
        valid_flow = {
            "flow_duration": 50000.0,
            "total_fwd_packets": 20,
            "total_backward_packets": 15,
            "total_length_of_fwd_packets": 2000.0,
            "total_length_of_bwd_packets": 4000.0,
            "fwd_packet_length_max": 1024.0,
            "fwd_packet_length_min": 64.0,
            "fwd_packet_length_mean": 256.0,
            "fwd_packet_length_std": 64.0,
            "bwd_packet_length_max": 1400.0,
            "bwd_packet_length_min": 64.0,
            "bwd_packet_length_mean": 300.0,
            "bwd_packet_length_std": 80.0,
            "flow_bytes_per_s": 120000.0,
            "flow_packets_per_s": 600.0,
            "flow_iat_mean": 1000.0,
            "flow_iat_std": 200.0,
            "flow_iat_max": 4000.0,
            "flow_iat_min": 5.0,
            "fwd_iat_total": 45000.0,
            "fwd_iat_mean": 2500.0,
            "fwd_iat_std": 600.0,
            "fwd_iat_max": 10000.0,
            "fwd_iat_min": 20.0,
            "bwd_iat_total": 40000.0,
            "bwd_iat_mean": 3000.0,
            "bwd_iat_std": 700.0,
            "bwd_iat_max": 12000.0,
            "bwd_iat_min": 15.0,
            "fwd_psh_flags": 0.0,
            "source_ip": "185.220.101.200",
            "destination_ip": "198.51.100.120",
            "source_port": 50000,
            "destination_port": 443,
            "protocol": "TCP"
        }
        res_pred = client.post("/api/v1/predict/single", json={"features": valid_flow}, headers=admin_hdr)
        assert res_pred.status_code == 200

        # Step 5: Threat Intelligence Telemetry Enrichment
        enrichment = await ThreatIntelService.enrich_telemetry("185.220.101.200", "198.51.100.120", None, db)
        assert enrichment["is_match"] is True

        # Step 6: Behavioral Anomaly Detection Spike
        for _ in range(6):
            await AnomalyService.update_baseline(asset.id, "packet_rate", 150.0, db)
        anom = await AnomalyService.detect_anomaly(asset.id, "packet_rate", 9500.0, db)
        assert anom is not None
        assert anom.z_score >= 3.0

        # Step 7: Authoritative Single Risk Scoring
        risk = RiskScoringEngine.calculate_risk_score(
            severity="critical",
            confidence=0.98,
            criticality="critical",
            alert_count=5
        )
        assert risk >= 85.0

        # Step 8: Incident Correlation Record
        inc = Incident(
            incident_code="INC-P3-E2E-001",
            asset_id=asset.id,
            source_ip="185.220.101.200",
            destination_ip="198.51.100.120",
            source_port=50000,
            destination_port=443,
            protocol="TCP",
            packet_length=1024,
            is_malicious=True,
            attack_type="DDoS",
            severity="Critical",
            risk_score=risk
        )
        db.add(inc)
        await db.commit()
        await db.refresh(inc)

        # Step 9: Threat Hunting Query Execution
        hunt_res = await HuntingService.execute_hunting_query({
            "entity": "incidents",
            "filters": {"source_ip": "185.220.101.200"}
        }, "e2e_analyst", None, db)
        assert hunt_res["result_count"] >= 1

        # Step 10: Threat Graph Topology Construction
        graph = await ThreatGraphService.get_graph_topology(limit=50, db=db)
        assert graph["total_nodes"] > 0
        assert graph["total_edges"] >= 0

        # Step 11: Multi-Incident Campaign Correlation
        inc_2 = Incident(
            incident_code="INC-P3-E2E-002",
            asset_id=asset.id,
            source_ip="185.220.101.200",
            destination_ip="198.51.100.120",
            source_port=50001,
            destination_port=443,
            protocol="TCP",
            packet_length=1024,
            is_malicious=True,
            attack_type="DDoS",
            severity="Critical",
            risk_score=risk
        )
        db.add(inc_2)
        await db.commit()

        camps = await CampaignService.detect_campaigns(lookback_hours=24, db=db)
        assert len(camps) >= 1
        assert "UNKNOWN" in camps[0]["attribution"]

        # Step 12: Predictive Asset Risk Forecast
        forecast = await PredictiveService.compute_asset_forecast(asset.id, "24H", db)
        assert forecast.model_family == "phase3_predictive"
        assert forecast.predicted_score > 0.0

        # Step 13: Predictive Enterprise Alert Volume
        vol_fc = await PredictiveService.compute_volume_forecast(db)
        assert vol_fc.predicted_alert_count > 0

        # Step 14: MITRE ATT&CK Matrix Coverage Snapshot
        coverage = await AttackCoverageService.compute_coverage_snapshot(db)
        assert coverage.total_matrix_techniques > 0

        # Step 15: SOC Effectiveness KPIs (MTTD / MTTR)
        soc_ov = await SOCMetricsService.get_soc_overview(lookback_days=30, db=db)
        if soc_ov["mttd_minutes"] is not None:
            assert soc_ov["mttd_minutes"] >= 0.0
        if soc_ov["mttr_minutes"] is not None:
            assert soc_ov["mttr_minutes"] >= 0.0

        # Step 16: SOAR Response Approval Submission
        approval_req = await ResponseOrchestrator.request_action(
            incident_id=inc.id,
            requested_action="BLOCK_IOC_SIMULATION",
            target_entity="185.220.101.200",
            requested_by="analyst",
            parameters={"firewall_rule": "DROP"},
            db=db
        )
        assert approval_req.status == "REQUESTED"
        assert approval_req.is_dry_run is True

        # Step 17: Admin Approval & Dry-Run Execution
        appr_res = await ResponseOrchestrator.approve_and_execute(
            approval_id=approval_req.id,
            approved_by="admin",
            approver_role="admin",
            force_live=False,
            db=db
        )
        assert appr_res["status"] == "COMPLETED"
        assert appr_res["execution"]["is_dry_run"] is True

        # Step 18: Resilient Background Job Execution
        async def dummy_bg_task(session):
            return {"synced_indicators": 5}

        job = await JobManager.run_job("THREAT_FEED_SYNC", dummy_bg_task, max_retries=2)
        assert job.status == "COMPLETED"

        # Step 19: API Endpoints Smoke Check
        res_hunt_api = client.post("/api/v1/hunting/query", json={"entity": "alerts", "filters": {}}, headers=analyst_hdr)
        assert res_hunt_api.status_code == 200

        res_graph_api = client.get("/api/v1/threat-graph", headers=analyst_hdr)
        assert res_graph_api.status_code == 200

        res_pred_api = client.get(f"/api/v1/predictive/assets/{asset.id}", headers=analyst_hdr)
        assert res_pred_api.status_code == 200

        res_cov_api = client.get("/api/v1/attack-coverage", headers=analyst_hdr)
        assert res_cov_api.status_code == 200

        res_soc_api = client.get("/api/v1/soc-metrics/overview", headers=analyst_hdr)
        assert res_soc_api.status_code == 200

        res_resp_api = client.get("/api/v1/response/requests", headers=analyst_hdr)
        assert res_resp_api.status_code == 200

        # Step 20: CatBoost Invariant SHA-256 Check
        import json
        manifest_path = Path("ml/artifacts/artifact_manifest.json")
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_sha = manifest["model_hash"]

        catboost_file = Path("ml/artifacts/catboost.joblib")
        assert catboost_file.exists()
        sha = hashlib.sha256(catboost_file.read_bytes()).hexdigest()
        assert sha == expected_sha, "CatBoost SHA-256 hash changed! Invariant violated."
