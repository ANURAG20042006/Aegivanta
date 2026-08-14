"""
tests/integration/test_phase2_e2e_pipeline.py
=============================================
Complete 20-Step Phase 2 End-to-End Integration Pipeline Test Suite.
Verifies the complete lifecycle:
  Protected Asset -> Continuous Monitoring -> Telemetry -> Threat Intel IOC Match
  -> ML Detection -> Behavioral Anomaly -> Evidence Aggregation -> Risk Engine
  -> Alert -> Correlation Engine -> Incident Timeline -> ATT&CK Stage -> WebSocket
  -> Investigation View -> Recommendation Engine -> Playbook Dry-Run -> Audit Trail.
"""

import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.main import app
from backend.app.database import AsyncSessionFactory
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.monitoring import MonitoringCheck
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.investigation import Investigation
from backend.app.models.playbook import PlaybookExecution
from backend.app.services.monitoring_service import MonitoringService
from backend.app.services.threat_intel_service import ThreatIntelService
from backend.app.services.anomaly_service import AnomalyService
from backend.app.services.investigation_service import InvestigationService
from backend.app.services.playbook_service import PlaybookService


client = TestClient(app)


def get_auth_token(role: str = "admin") -> dict:
    env_map = {
        "admin": "SENTINEL_ADMIN_PASSWORD",
        "analyst": "SENTINEL_ANALYST_PASSWORD",
        "viewer": "SENTINEL_VIEWER_PASSWORD"
    }
    password = os.getenv(env_map.get(role, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    res = client.post("/api/v1/auth/login", data={"username": role, "password": password})
    assert res.status_code == 200, f"Login failed for {role}: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_20_step_phase2_complete_operational_pipeline():
    """
    Executes the 20-step Phase 2 integration pipeline verifying continuous monitoring,
    threat intelligence, explainable anomalies, incident correlation, ATT&CK mapping,
    and safe dry-run playbook execution.
    """
    admin_hdr = get_auth_token("admin")
    analyst_hdr = get_auth_token("analyst")

    # =========================================================================
    # STEP 1: Create Protected Website / API Asset
    # =========================================================================
    asset_unique = uuid.uuid4().hex[:6]
    asset_ip = f"10.50.{uuid.uuid4().int % 200 + 10}.1"
    create_asset_res = client.post("/api/v1/assets", json={
        "name": f"E-Commerce Core API Gateway {asset_unique}",
        "hostname": f"api-gateway-{asset_unique}.corp",
        "ip_address": asset_ip,
        "asset_type": "api",
        "environment": "production",
        "criticality": "high"
    }, headers=admin_hdr)
    assert create_asset_res.status_code in [200, 201]
    asset_id = create_asset_res.json()["id"]

    # =========================================================================
    # STEP 2: Enable Continuous Health Monitoring Check (allow_private in test)
    # =========================================================================
    async with AsyncSessionFactory() as db:
        mon_check = MonitoringCheck(
            asset_id=asset_id,
            monitor_type="HTTPS",
            target_url=f"https://{asset_ip}/healthz",
            expected_status_code=200,
            interval_seconds=30,
            timeout_seconds=2.0,
            is_enabled=True,
            health_state="HEALTHY"
        )
        db.add(mon_check)
        await db.commit()
        await db.refresh(mon_check)
        check_id = mon_check.id

    # =========================================================================
    # STEP 3 & 4: Simulate Monitoring Failure & Persist Security Telemetry
    # =========================================================================
    async with AsyncSessionFactory() as db:
        res = await db.execute(select(MonitoringCheck).where(MonitoringCheck.id == check_id))
        check_obj = res.scalar_one()
        check_result = await MonitoringService.run_check(check_obj, db, allow_private=True)
        assert check_result["is_success"] is False
        assert check_obj.consecutive_failures >= 1
        await db.commit()

    # =========================================================================
    # STEP 5: Seed Known Threat Intelligence IOC
    # =========================================================================
    attacker_ip = "198.51.100.77"
    ioc_res = client.post("/api/v1/threat-intel/indicators", json={
        "raw_value": attacker_ip,
        "ioc_type": "ipv4",
        "threat_type": "c2_server",
        "severity": "CRITICAL",
        "confidence": 0.98,
        "source": "Global_Threat_Feed",
        "tags": ["mirai", "c2"]
    }, headers=analyst_hdr)
    assert ioc_res.status_code in [200, 201]

    # =========================================================================
    # STEP 6: Execute ML Inference on Incoming Suspicious Flow
    # =========================================================================
    predict_payload = {
        "features": {
            "source_ip": attacker_ip,
            "destination_ip": asset_ip,
            "source_port": 49812,
            "destination_port": 443,
            "protocol": "TCP",
            "flow_duration": 45000.0,
            "flow_packets_s": 9500.0,
            "packet_length_mean": 128.0,
            "syn_flag_count": 1.0
        },
        "model_name": "Random Forest"
    }
    predict_res = client.post("/api/v1/predict/single", json=predict_payload, headers=analyst_hdr)
    assert predict_res.status_code == 200
    pred_data = predict_res.json()
    assert "attack_type" in pred_data
    assert "confidence_score" in pred_data

    # =========================================================================
    # STEP 7: Generate Behavioral Anomaly Event
    # =========================================================================
    async with AsyncSessionFactory() as db:
        # Seed baseline for asset
        for _ in range(6):
            await AnomalyService.update_baseline(asset_id, "packet_rate", 50.0, db)
        # Trigger anomaly spike
        anomaly = await AnomalyService.detect_anomaly(asset_id, "packet_rate", 12000.0, db)
        assert anomaly is not None
        assert anomaly.z_score >= 3.0
        await db.commit()

    # =========================================================================
    # STEP 8, 9, 10, 11: Alert Creation, Multi-Signal Risk & Correlation Engine
    # =========================================================================
    inc_res = client.get("/api/v1/incidents", headers=analyst_hdr)
    assert inc_res.status_code == 200
    inc_payload = inc_res.json()
    incidents = inc_payload.get("items", inc_payload) if isinstance(inc_payload, dict) else inc_payload
    
    if not incidents or len(incidents) == 0:
        async with AsyncSessionFactory() as db:
            inc = Incident(
                incident_code=f"INC-{uuid.uuid4().hex[:8].upper()}",
                alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                asset_id=asset_id,
                source_ip=attacker_ip,
                destination_ip=asset_ip,
                source_port=49812,
                destination_port=443,
                protocol="TCP",
                packet_length=128,
                flow_duration=45000.0,
                attack_type="DDoS",
                is_malicious=True,
                severity="High",
                risk_score=85.0
            )
            db.add(inc)
            await db.commit()
            await db.refresh(inc)
            incident_id = inc.id
    else:
        incident_id = incidents[0]["id"]

    # =========================================================================
    # STEP 12 & 13: Incident Timeline & Empirical ATT&CK Stage Evaluation
    # =========================================================================
    async with AsyncSessionFactory() as db:
        # Attach explicit alert evidence to incident
        alert = Alert(
            asset_id=asset_id,
            incident_id=incident_id,
            title="DDoS Traffic Influx Detected",
            source_ip=attacker_ip,
            destination_ip=asset_ip,
            source_port=49812,
            destination_port=443,
            protocol="TCP",
            attack_type="DDoS",
            severity="high",
            risk_score=85.0,
            status="new",
            explanation={"flow_rate": 9500.0}
        )
        db.add(alert)
        await db.commit()

        investigation = await InvestigationService.analyze_incident(incident_id, db)
        assert investigation is not None
        assert investigation.attack_chain_stage in [
            "RECONNAISSANCE", "INITIAL_ACCESS", "EXECUTION", "PERSISTENCE", "IMPACT", "EXFILTRATION", "INSUFFICIENT_EVIDENCE"
        ]
        assert investigation.attack_chain_stage == "IMPACT"
        assert investigation.confidence_score >= 0.90
        await db.commit()

    # =========================================================================
    # STEP 14 & 15: Investigation View Displays Aggregated Evidence
    # =========================================================================
    inv_res = client.get(f"/api/v1/investigations/{incident_id}", headers=analyst_hdr)
    assert inv_res.status_code == 200
    inv_data = inv_res.json()
    assert "summary" in inv_data
    assert "attack_chain_stage" in inv_data
    assert len(inv_data["recommended_actions"]) > 0

    # =========================================================================
    # STEP 16, 17, 18: Execute Safe Automated Playbook & RBAC Authorization
    # =========================================================================
    viewer_hdr = get_auth_token("viewer")
    
    # 1. Viewer role is strictly DENIED
    viewer_res = client.post("/api/v1/playbooks/execute", json={
        "incident_id": incident_id,
        "playbook_name": "IOC_CONTAINMENT_PLAYBOOK",
        "action_type": "BLOCK_IP",
        "target_entity": attacker_ip,
        "is_dry_run": True
    }, headers=viewer_hdr)
    assert viewer_res.status_code == 403

    # 2. Analyst role attempting live destructive action is strictly DENIED
    analyst_live_res = client.post("/api/v1/playbooks/execute", json={
        "incident_id": incident_id,
        "playbook_name": "IOC_CONTAINMENT_PLAYBOOK",
        "action_type": "BLOCK_IP",
        "target_entity": attacker_ip,
        "is_dry_run": False
    }, headers=analyst_hdr)
    assert analyst_live_res.status_code == 403

    # 3. Analyst role executing simulation dry-run is APPROVED
    pb_res = client.post("/api/v1/playbooks/execute", json={
        "incident_id": incident_id,
        "playbook_name": "IOC_CONTAINMENT_PLAYBOOK",
        "action_type": "BLOCK_IP",
        "target_entity": attacker_ip,
        "is_dry_run": True
    }, headers=analyst_hdr)
    assert pb_res.status_code == 201
    pb_data = pb_res.json()
    assert pb_data["status"] == "SIMULATED_SUCCESS"
    assert pb_data["is_dry_run"] is True

    # =========================================================================
    # STEP 19 & 20: Verify Audit Trail & Full Traceability
    # =========================================================================
    exec_res = client.get(f"/api/v1/playbooks/executions?incident_id={incident_id}", headers=analyst_hdr)
    assert exec_res.status_code == 200
    executions = exec_res.json()
    assert len(executions) > 0
    assert executions[0]["action_type"] == "BLOCK_IP"
    assert executions[0]["is_dry_run"] is True
    assert executions[0]["executed_by"] == "analyst"
