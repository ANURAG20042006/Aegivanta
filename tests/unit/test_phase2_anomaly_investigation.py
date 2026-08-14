"""
tests/unit/test_phase2_anomaly_investigation.py
===============================================
Unit Tests for Behavioral Baselines, Zero-Variance Protection,
Evidence-Based MITRE ATT&CK Mapping, and Playbook Authorization Safety.
"""

import pytest
from backend.app.services.anomaly_service import AnomalyService
from backend.app.services.investigation_service import evaluate_attack_chain_stage, ATTACK_TACTIC_RULES
from backend.app.services.playbook_service import PlaybookService
from backend.app.database import AsyncSessionFactory


@pytest.mark.asyncio
async def test_anomaly_detection_cold_start_handling():
    """Verify that fewer than 5 baseline observations do not trigger false positive anomalies."""
    async with AsyncSessionFactory() as db:
        from backend.app.models.protected_asset import ProtectedAsset
        asset = ProtectedAsset(
            name="Cold Start Test Asset",
            hostname="cold-start.corp",
            ip_address="10.99.1.6",
            asset_type="server",
            criticality="medium"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        # First 3 samples
        for val in [10.0, 12.0, 11.0]:
            anomaly = await AnomalyService.detect_anomaly(asset.id, "request_rate", val, db)
            assert anomaly is None, "Cold start baseline should not trigger an anomaly event."
        await db.commit()


@pytest.mark.asyncio
async def test_anomaly_detection_triggers_on_large_deviation():
    """Verify that a metric spike > 3 sigma above baseline triggers an explainable AnomalyEvent."""
    async with AsyncSessionFactory() as db:
        from backend.app.models.protected_asset import ProtectedAsset
        asset = ProtectedAsset(
            name="Anomaly Test Asset",
            hostname="anomaly-test.corp",
            ip_address="10.99.1.5",
            asset_type="server",
            criticality="high"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        # Seed 6 baseline samples around mean ~ 10.0
        for _ in range(6):
            await AnomalyService.update_baseline(asset.id, "destination_diversity", 10.0, db)
        await db.commit()

        # Observed massive spike
        anomaly = await AnomalyService.detect_anomaly(asset.id, "destination_diversity", 150.0, db)
        assert anomaly is not None
        assert anomaly.z_score >= 3.0
        assert anomaly.anomaly_score >= 50.0
        assert "destination_diversity" in anomaly.explanation
        assert "baseline" in anomaly.explanation
        assert "SPIKE_INCREASE" in anomaly.explanation
        await db.commit()


def test_mitre_attack_stage_evidence_based_mapping():
    """Verify empirical evidence rule evaluation and INSUFFICIENT_EVIDENCE fallback."""
    # 1. Clear evidence of PortScan
    stage, conf, summary, details = evaluate_attack_chain_stage(
        attack_type="PortScan",
        alerts_count=2,
        ioc_matches_count=1,
        anomaly_count=1,
        risk_score=75.0
    )
    assert stage == "RECONNAISSANCE"
    assert conf >= 0.90
    assert "TA0043" in details["tactic_id"]

    # 2. Clear evidence of DDoS
    stage_ddos, conf_ddos, _, details_ddos = evaluate_attack_chain_stage(
        attack_type="DDoS",
        alerts_count=3,
        ioc_matches_count=1,
        anomaly_count=1,
        risk_score=90.0
    )
    assert stage_ddos == "IMPACT"
    assert "TA0040" in details_ddos["tactic_id"]

    # 3. Benign or No Evidence -> INSUFFICIENT_EVIDENCE (Never invented!)
    stage_none, conf_none, summary_none, _ = evaluate_attack_chain_stage(
        attack_type="BENIGN",
        alerts_count=0,
        ioc_matches_count=0,
        anomaly_count=0,
        risk_score=0.0
    )
    assert stage_none == "INSUFFICIENT_EVIDENCE"
    assert conf_none <= 0.50
    assert "Insufficient" in summary_none


@pytest.mark.asyncio
async def test_playbook_service_defaults_to_dry_run_simulation():
    """Verify playbook execution defaults to dry-run simulation mode with audit records."""
    async with AsyncSessionFactory() as db:
        from backend.app.models.incident import Incident
        inc = Incident(
            incident_code="INC-PLAYBOOK-TEST",
            source_ip="198.51.100.99",
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
        await db.flush()

        res = await PlaybookService.execute_action(
            incident_id=inc.id,
            playbook_name="TEST_CONTAINMENT_PLAYBOOK",
            action_type="BLOCK_IP",
            target_entity="198.51.100.99",
            is_dry_run=True,
            parameters={"actor_role": "analyst"},
            db=db
        )

        assert res["status"] == "SIMULATED_SUCCESS"
        assert res["is_dry_run"] is True
        assert "[SIMULATION DRY RUN]" in res["log"]
        await db.commit()
