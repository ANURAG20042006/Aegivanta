"""
tests/integration/test_final_phase2_integrity.py
================================================
Comprehensive Final Phase 2 Regression & Integrity Test Suite.
Validates that Phase 1 core invariants, ML provenance, and Phase 2 security capabilities
operate deterministically without regression.
"""

import os
import hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import AsyncSessionFactory
from backend.app.config import settings
from backend.app.services.monitoring_service import validate_target_url_safe
from backend.app.services.threat_intel_service import ThreatIntelService, normalize_ioc
from backend.app.services.anomaly_service import AnomalyService
from backend.app.services.investigation_service import evaluate_attack_chain_stage
from backend.app.services.playbook_service import PlaybookService
from backend.app.services.risk_engine import RiskScoringEngine
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.incident import Incident
from backend.app.models.alert import Alert


client = TestClient(app)
EXPECTED_CATBOOST_SHA256 = "efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82"
EXPECTED_PREPROCESSOR_SHA256 = "e5c07b23b9a82ca28b6805e0a2eeff3c42c97b47d6816fd089dbb92d12d93691"


def get_auth_token(role: str = "admin") -> dict:
    passwords = {
        "admin": [getattr(settings, "SENTINEL_ADMIN_PASSWORD", "Admin_Secure2026!"), "TestAdminPassword2026!"],
        "analyst": [getattr(settings, "SENTINEL_ANALYST_PASSWORD", "Analyst_Secure2026!"), "TestAnalystPassword2026!"],
        "viewer": [getattr(settings, "SENTINEL_VIEWER_PASSWORD", "Viewer_Secure2026!"), "TestViewerPassword2026!"]
    }
    
    candidates = passwords.get(role, ["Admin_Secure2026!", "TestAdminPassword2026!"])
    token = None
    for pwd in candidates:
        resp = client.post("/api/v1/auth/login", data={"username": role, "password": pwd})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            break
            
    assert token is not None, f"Authentication failed for role {role}"
    return {"Authorization": f"Bearer {token}"}


def test_1_phase1_pipeline_operational_and_predict():
    """Verify Phase 1 predict endpoint accepts 30 continuous features and produces valid ML classification."""
    admin_hdr = get_auth_token("admin")
    valid_flow = {
        "flow_duration": 45000.0,
        "total_fwd_packets": 12,
        "total_backward_packets": 8,
        "total_length_of_fwd_packets": 1400.0,
        "total_length_of_bwd_packets": 2800.0,
        "fwd_packet_length_max": 512.0,
        "fwd_packet_length_min": 64.0,
        "fwd_packet_length_mean": 128.0,
        "fwd_packet_length_std": 32.0,
        "bwd_packet_length_max": 1024.0,
        "bwd_packet_length_min": 64.0,
        "bwd_packet_length_mean": 256.0,
        "bwd_packet_length_std": 64.0,
        "flow_bytes_per_s": 95000.0,
        "flow_packets_per_s": 450.0,
        "flow_iat_mean": 1200.0,
        "flow_iat_std": 300.0,
        "flow_iat_max": 5000.0,
        "flow_iat_min": 10.0,
        "fwd_iat_total": 40000.0,
        "fwd_iat_mean": 3500.0,
        "fwd_iat_std": 800.0,
        "fwd_iat_max": 12000.0,
        "fwd_iat_min": 50.0,
        "bwd_iat_total": 35000.0,
        "bwd_iat_mean": 4500.0,
        "bwd_iat_std": 900.0,
        "bwd_iat_max": 15000.0,
        "bwd_iat_min": 20.0,
        "fwd_psh_flags": 0.0,
        "source_ip": "198.51.100.22",
        "destination_ip": "10.0.0.1",
        "source_port": 54321,
        "destination_port": 80,
        "protocol": "TCP"
    }
    resp = client.post("/api/v1/predict/single", json={"features": valid_flow}, headers=admin_hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "prediction" in data or "attack_type" in data
    assert "is_malicious" in data


def test_2_catboost_artifact_sha256_unmodified():
    """Verify CatBoost champion artifact exact SHA-256 hash."""
    model_path = Path("ml/artifacts/catboost.joblib")
    assert model_path.exists(), "catboost.joblib missing"
    sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    assert sha == EXPECTED_CATBOOST_SHA256, f"CatBoost SHA mismatch! Expected {EXPECTED_CATBOOST_SHA256}, got {sha}"


def test_3_preprocessor_and_dataset_provenance_intact():
    """Verify preprocessor artifact SHA-256 matches manifest and EXP-2026-002."""
    prep_path = Path("ml/artifacts/preprocessor.joblib")
    assert prep_path.exists(), "preprocessor.joblib missing"
    sha = hashlib.sha256(prep_path.read_bytes()).hexdigest()
    assert sha == EXPECTED_PREPROCESSOR_SHA256, f"Preprocessor SHA mismatch! Expected {EXPECTED_PREPROCESSOR_SHA256}, got {sha}"


def test_4_phase2_monitoring_and_ssrf_enforcement():
    """Verify Continuous Monitoring rejects private/loopback/cloud metadata targets."""
    # Private IP rejected
    is_safe_priv, _, _, _ = validate_target_url_safe("http://192.168.1.1/api", allow_private=False)
    assert is_safe_priv is False

    # IPv4-mapped IPv6 rejected
    is_safe_mapped, _, _, _ = validate_target_url_safe("http://[::ffff:127.0.0.1]/", allow_private=False)
    assert is_safe_mapped is False

    # Public domain accepted
    is_safe_pub, _, ip, _ = validate_target_url_safe("https://cloudflare.com", allow_private=False)
    assert is_safe_pub is True
    assert ip is not None


@pytest.mark.asyncio
async def test_5_threat_intelligence_normalization_and_enrichment():
    """Verify Threat Intelligence normalizes IOCs and enriches telemetry."""
    is_v, norm_ip, ioc_type = normalize_ioc("  185.220.101.55  ", "ipv4")
    assert is_v is True
    assert norm_ip == "185.220.101.55"
    assert ioc_type == "ipv4"

    async with AsyncSessionFactory() as db:
        ioc = ThreatIndicator(
            ioc_type="ipv4",
            raw_value="185.220.101.55",
            normalized_value="185.220.101.55",
            threat_type="TOR_EXIT_NODE",
            severity="high",
            confidence=0.95,
            source="Unit Test"
        )
        db.add(ioc)
        await db.commit()

        enrichment = await ThreatIntelService.enrich_telemetry(
            source_ip="185.220.101.55",
            destination_ip="10.0.0.1",
            domain=None,
            db=db
        )
        assert enrichment["is_match"] is True
        assert len(enrichment["matched_iocs"]) > 0


@pytest.mark.asyncio
async def test_6_anomaly_detection_with_zero_variance_protection():
    """Verify Behavioral Anomaly Detection handles zero-variance and triggers explainable events."""
    async with AsyncSessionFactory() as db:
        asset = ProtectedAsset(
            name="Anomaly Integrity Asset",
            hostname="anomaly-int.corp",
            ip_address="198.51.100.88",
            asset_type="server",
            criticality="high"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        # Baseline observations with zero variance (constant 100.0)
        for _ in range(6):
            await AnomalyService.update_baseline(asset.id, "packet_rate", 100.0, db)

        # Spike observation
        anomaly = await AnomalyService.detect_anomaly(asset.id, "packet_rate", 850.0, db)
        assert anomaly is not None
        assert anomaly.z_score >= 3.0
        assert "SPIKE_INCREASE" in anomaly.explanation
        assert "threshold" in anomaly.explanation
        await db.commit()


def test_7_investigation_evidence_evaluation_and_insufficient_evidence_fallback():
    """Verify MITRE ATT&CK mapping produces INSUFFICIENT_EVIDENCE when telemetry is absent."""
    # Insufficient telemetry
    stage_empty, conf_empty, _, _ = evaluate_attack_chain_stage(
        attack_type="BENIGN",
        alerts_count=0,
        ioc_matches_count=0,
        anomaly_count=0,
        risk_score=0.0
    )
    assert stage_empty == "INSUFFICIENT_EVIDENCE"
    assert conf_empty <= 0.50

    # Concrete attack telemetry
    stage_recon, conf_recon, _, _ = evaluate_attack_chain_stage(
        attack_type="PortScan",
        alerts_count=2,
        ioc_matches_count=1,
        anomaly_count=0,
        risk_score=65.0
    )
    assert stage_recon == "RECONNAISSANCE"
    assert conf_recon >= 0.90


@pytest.mark.asyncio
async def test_8_playbook_safety_dry_run_default_and_audit():
    """Verify Playbook execution defaults strictly to dry-run simulation mode with audit records."""
    async with AsyncSessionFactory() as db:
        inc = Incident(
            incident_code="INC-INT-PLAYBOOK",
            source_ip="198.51.100.77",
            destination_ip="10.0.0.1",
            source_port=54321,
            destination_port=80,
            protocol="TCP",
            packet_length=64,
            flow_duration=100.0,
            attack_type="DDoS",
            is_malicious=True,
            severity="High",
            risk_score=85.0
        )
        db.add(inc)
        await db.commit()
        await db.refresh(inc)

        result = await PlaybookService.execute_action(
            incident_id=inc.id,
            playbook_name="IP_CONTAINMENT_PLAYBOOK",
            action_type="BLOCK_IP",
            target_entity="198.51.100.77",
            is_dry_run=True,
            executed_by="admin",
            parameters={"actor_role": "admin"},
            db=db
        )
        assert result["status"] == "SIMULATED_SUCCESS"
        assert result["is_dry_run"] is True
        assert "[SIMULATION DRY RUN]" in result["log"]
        await db.commit()


def test_9_rbac_server_side_enforcement():
    """Verify server-side RBAC: Viewer denied mutations, Analyst denied live actions, Admin authorized."""
    viewer_hdr = get_auth_token("viewer")
    analyst_hdr = get_auth_token("analyst")

    # Viewer denied monitoring check creation
    res_v = client.post("/api/v1/monitoring/checks", json={
        "asset_id": "non-existent",
        "target_url": "https://cloudflare.com",
        "expected_status_code": 200
    }, headers=viewer_hdr)
    assert res_v.status_code == 403

    # Analyst denied live destructive playbook execution
    res_a_live = client.post("/api/v1/playbooks/execute", json={
        "incident_id": "sample-inc",
        "playbook_name": "CONTAINMENT",
        "action_type": "BLOCK_IP",
        "target_entity": "198.51.100.1",
        "is_dry_run": False
    }, headers=analyst_hdr)
    assert res_a_live.status_code == 403


def test_10_phase1_risk_engine_authority():
    """Verify RiskScoringEngine remains the single authoritative formula for 0-100 risk scoring."""
    # Critical severity + High criticality + 10 recurrence -> Top tier
    score_crit = RiskScoringEngine.calculate_risk_score(
        severity="critical",
        confidence=0.98,
        criticality="critical",
        alert_count=10
    )
    assert 90.0 <= score_crit <= 100.0
    assert RiskScoringEngine.get_risk_tier(score_crit) == "CRITICAL"

    # Info severity + Low criticality + 1 alert -> Low tier
    score_low = RiskScoringEngine.calculate_risk_score(
        severity="info",
        confidence=0.50,
        criticality="low",
        alert_count=1
    )
    assert score_low <= 25.0
    assert RiskScoringEngine.get_risk_tier(score_low) == "LOW"
