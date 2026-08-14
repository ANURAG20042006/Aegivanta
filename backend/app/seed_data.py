"""
backend/app/seed_data.py
========================
Deterministic Demo Data Seeder for SentinelAI SOC Platform (Phase 1 & Phase 2).
Populates realistic Protected Assets, Monitoring Checks, Threat Indicators,
Behavioral Baselines, Anomalies, Incidents, Alerts, and Investigation Records.
"""

import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.monitoring import MonitoringCheck, MonitoringHistory
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.behavioral import BehavioralBaseline, AnomalyEvent
from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.models.investigation import Investigation, InvestigationEvidence
from backend.app.models.playbook import PlaybookExecution
from backend.app.core.logging import logger


async def seed_demo_operational_data(db: AsyncSession) -> None:
    """Seeds rich operational data for demo and development environments if tables are empty."""
    asset_count = (await db.execute(select(func.count(ProtectedAsset.id)))).scalar_one()
    if asset_count > 0:
        return

    logger.info("Seeding Phase 1 & Phase 2 operational demo dataset...")
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # 1. Protected Assets
    assets_data = [
        ("api-gateway", "E-Commerce Core API Gateway", "api.sentinelai.io", "198.51.100.10", "api", "critical", "Production REST API Gateway"),
        ("auth-svc", "Corporate Authentication Service", "auth.sentinelai.io", "198.51.100.20", "server", "critical", "OAuth2 / SAML Auth Service"),
        ("db-master", "Database Master Cluster", "db.sentinelai.io", "198.51.100.40", "database", "critical", "Primary Transaction DB"),
        ("web-frontend", "Public Customer Portal", "sentinelai.io", "198.51.100.50", "website", "medium", "Public Web Application")
    ]
    
    asset_objs = {}
    for code, name, host, ip, a_type, crit, desc in assets_data:
        asset = ProtectedAsset(
            name=name,
            hostname=host,
            ip_address=ip,
            asset_type=a_type,
            criticality=crit,
            owner="Security Operations",
            environment="production",
            description=desc,
            created_at=now
        )
        db.add(asset)
        asset_objs[code] = asset

    await db.flush()

    # 2. Continuous Monitoring Checks
    check_1 = MonitoringCheck(
        asset_id=asset_objs["web-frontend"].id,
        monitor_type="HTTP",
        target_url="https://cloudflare.com",
        expected_status_code=200,
        timeout_seconds=5,
        interval_seconds=30,
        health_state="HEALTHY",
        consecutive_failures=0,
        last_check_at=now,
        last_status_code=200,
        last_response_time_ms=38.4,
        dns_resolved_ip="104.16.132.229",
        created_at=now
    )
    check_2 = MonitoringCheck(
        asset_id=asset_objs["api-gateway"].id,
        monitor_type="HTTP",
        target_url="https://httpbin.org/status/200",
        expected_status_code=200,
        timeout_seconds=5,
        interval_seconds=30,
        health_state="HEALTHY",
        consecutive_failures=0,
        last_check_at=now,
        last_status_code=200,
        last_response_time_ms=82.1,
        dns_resolved_ip="54.161.240.231",
        created_at=now
    )
    check_3 = MonitoringCheck(
        asset_id=asset_objs["auth-svc"].id,
        monitor_type="HTTP",
        target_url="https://httpbin.org/status/503",
        expected_status_code=200,
        timeout_seconds=5,
        interval_seconds=30,
        health_state="DOWN",
        consecutive_failures=3,
        last_check_at=now,
        last_status_code=503,
        last_response_time_ms=114.6,
        last_error_message="HTTP status 503 != expected 200",
        dns_resolved_ip="54.161.240.231",
        created_at=now
    )
    db.add_all([check_1, check_2, check_3])
    await db.flush()

    # History entries
    db.add(MonitoringHistory(
        check_id=check_1.id,
        asset_id=asset_objs["web-frontend"].id,
        timestamp=now,
        status_code=200,
        response_time_ms=38.4,
        is_success=True
    ))
    db.add(MonitoringHistory(
        check_id=check_3.id,
        asset_id=asset_objs["auth-svc"].id,
        timestamp=now,
        status_code=503,
        response_time_ms=114.6,
        is_success=False,
        error_message="HTTP status 503 != expected 200"
    ))

    # 3. Threat Intelligence Indicators
    threat_indicators = [
        ThreatIndicator(
            ioc_type="ipv4",
            raw_value="185.220.101.5",
            normalized_value="185.220.101.5",
            threat_type="TOR_EXIT_NODE",
            severity="high",
            confidence=0.95,
            source="Tor Project Directory",
            description="Active Tor Exit Node observed probing enterprise endpoints",
            tags=["tor", "proxy", "reconnaissance"],
            hit_count=42,
            last_seen=now,
            created_at=now
        ),
        ThreatIndicator(
            ioc_type="ipv4",
            raw_value="45.154.255.89",
            normalized_value="45.154.255.89",
            threat_type="C2_SERVER",
            severity="critical",
            confidence=0.98,
            source="Emerging Threats IP Blocklist",
            description="Command and Control (C2) server associated with botnet operations",
            tags=["c2", "botnet", "malware"],
            hit_count=18,
            last_seen=now,
            created_at=now
        ),
        ThreatIndicator(
            ioc_type="domain",
            raw_value="botnet-c2-payload.org",
            normalized_value="botnet-c2-payload.org",
            threat_type="BOTNET_C2",
            severity="critical",
            confidence=0.92,
            source="ThreatFox Abuse.ch",
            description="Active botnet payload staging domain",
            tags=["c2", "domain", "fast-flux"],
            hit_count=5,
            last_seen=now,
            created_at=now
        )
    ]
    db.add_all(threat_indicators)

    # 4. Behavioral Baselines & Anomaly Events
    db.add(BehavioralBaseline(
        asset_id=asset_objs["api-gateway"].id,
        metric_name="packet_rate",
        baseline_mean=120.0,
        baseline_std=15.0,
        min_val=40.0,
        max_val=210.0,
        sample_count=85,
        updated_at=now
    ))
    db.add(BehavioralBaseline(
        asset_id=asset_objs["api-gateway"].id,
        metric_name="byte_volume",
        baseline_mean=48000.0,
        baseline_std=3500.0,
        min_val=15000.0,
        max_val=82000.0,
        sample_count=85,
        updated_at=now
    ))
    
    anomaly = AnomalyEvent(
        asset_id=asset_objs["api-gateway"].id,
        timestamp=now,
        metric_name="packet_rate",
        observed_value=12500.0,
        baseline_mean=120.0,
        baseline_std=15.0,
        z_score=825.33,
        anomaly_score=98.5,
        severity="CRITICAL",
        explanation="Metric 'packet_rate' (12500.0) increased 104.2x [SPIKE_INCREASE] relative to asset baseline (120.0 ± 15.0, z-score: 825.33, threshold: 3.0σ).",
        status="ACTIVE"
    )
    db.add(anomaly)
    await db.flush()

    # 5. Incidents, Correlated Alerts & Timelines
    inc = Incident(
        incident_code="INC-2026-001",
        alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        asset_id=asset_objs["api-gateway"].id,
        title="DDoS Volumetric Flooding Attack targeting API Gateway",
        description="High-volume packet flood detected from known malicious botnet infrastructure.",
        source_ip="45.154.255.89",
        destination_ip="198.51.100.10",
        source_port=58912,
        destination_port=443,
        protocol="TCP",
        packet_length=1420,
        flow_duration=95000.0,
        attack_type="DDoS",
        confidence_score=0.96,
        is_malicious=True,
        severity="High",
        risk_score=88.5,
        alert_count=8,
        status="INVESTIGATING",
        timestamp=now,
        first_seen=now - timedelta(minutes=15),
        last_seen=now
    )
    db.add(inc)
    await db.flush()

    # Alerts associated with Incident
    alt_1 = Alert(
        asset_id=asset_objs["api-gateway"].id,
        incident_id=inc.id,
        title="DDoS TCP SYN Flood Signature Detected",
        source_ip="45.154.255.89",
        destination_ip="198.51.100.10",
        source_port=58912,
        destination_port=443,
        protocol="TCP",
        attack_type="DDoS",
        severity="high",
        risk_score=88.5,
        status="correlated",
        explanation={"top_feature": "flow_packets_per_s", "importance": 0.38},
        timestamp=now - timedelta(minutes=10)
    )
    alt_2 = Alert(
        asset_id=asset_objs["api-gateway"].id,
        incident_id=inc.id,
        title="Threat Intelligence Attribution: Known C2 Host",
        source_ip="45.154.255.89",
        destination_ip="198.51.100.10",
        source_port=58912,
        destination_port=443,
        protocol="TCP",
        attack_type="DDoS",
        severity="critical",
        risk_score=94.0,
        status="correlated",
        explanation={"ioc": "45.154.255.89", "threat_type": "C2_SERVER"},
        timestamp=now - timedelta(minutes=5)
    )
    db.add_all([alt_1, alt_2])

    # Incident Timeline
    db.add(IncidentTimelineEvent(
        incident_id=inc.id,
        event_type="DETECTION",
        title="ML Attack Detection",
        description="CatBoost model classified flow telemetry as DDoS with 96% confidence.",
        actor="CatBoost Champion ML Engine",
        metadata_payload={"model": "CatBoost", "confidence": 0.96},
        timestamp=now - timedelta(minutes=15)
    ))
    db.add(IncidentTimelineEvent(
        incident_id=inc.id,
        event_type="CORRELATION",
        title="Threat Intel IOC Correlated",
        description="Source IP 45.154.255.89 matched active C2_SERVER threat indicator.",
        actor="Threat Intelligence Service",
        metadata_payload={"ioc": "45.154.255.89"},
        timestamp=now - timedelta(minutes=10)
    ))
    db.add(IncidentTimelineEvent(
        incident_id=inc.id,
        event_type="ANOMALY",
        title="Behavioral Metric Spike Correlated",
        description="Asset traffic packet_rate exceeded baseline by 825.33σ.",
        actor="Anomaly Detection Service",
        metadata_payload={"z_score": 825.33},
        timestamp=now - timedelta(minutes=5)
    ))

    # 6. Automated Investigation Record
    investigation = Investigation(
        incident_id=inc.id,
        asset_id=asset_objs["api-gateway"].id,
        status="COMPLETED",
        summary="Automated investigation for incident INC-2026-001: Correlated 8 alert(s) classified as 'DDoS' with operational risk score 88.5/100. Empirical evidence attributes this incident to MITRE ATT&CK Stage [IMPACT] via technique 'Network Denial of Service (T1498)'.",
        findings={
            "incident_code": "INC-2026-001",
            "total_alerts": 8,
            "primary_threat": "DDoS",
            "source_ip": "45.154.255.89",
            "destination_ip": "198.51.100.10",
            "risk_score": 88.5,
            "ioc_hits_count": 1,
            "anomaly_events_count": 1
        },
        attack_chain_stage="IMPACT",
        confidence_score=0.95,
        recommended_actions=[
            "Review perimeter firewall rules and connection tables for source IP 45.154.255.89.",
            "Inspect system health and error telemetry for protected asset E-Commerce Core API Gateway.",
            "Execute IP containment playbook for known malicious indicator 45.154.255.89.",
            "High operational risk score detected (>70.0) — elevate incident priority to Tier-2 SOC review."
        ],
        created_at=now,
        updated_at=now
    )
    db.add(investigation)
    await db.flush()

    # Evidence items
    db.add(InvestigationEvidence(
        investigation_id=investigation.id,
        evidence_type="ALERT",
        reference_id=alt_1.id,
        description="Correlated Alert (DDoS, severity: high, risk_score: 88.5)",
        timestamp=alt_1.timestamp,
        metadata_json={"alert_id": alt_1.id, "risk_score": alt_1.risk_score}
    ))
    db.add(InvestigationEvidence(
        investigation_id=investigation.id,
        evidence_type="IOC_MATCH",
        reference_id=threat_indicators[1].id,
        description="Threat Intelligence IOC match: 45.154.255.89 (C2_SERVER, source: Emerging Threats IP Blocklist)",
        timestamp=now,
        metadata_json={"confidence": 0.98}
    ))
    db.add(InvestigationEvidence(
        investigation_id=investigation.id,
        evidence_type="BEHAVIORAL_ANOMALY",
        reference_id=anomaly.id,
        description="Behavioral Anomaly: packet_rate spike (12500.0 vs 120.0 baseline, z-score: 825.33)",
        timestamp=now,
        metadata_json={"metric": "packet_rate", "z_score": 825.33}
    ))

    # 7. Playbook Simulation Execution
    db.add(PlaybookExecution(
        incident_id=inc.id,
        playbook_name="IP_CONTAINMENT_PLAYBOOK",
        action_type="BLOCK_IP",
        is_dry_run=True,
        target_entity="45.154.255.89",
        parameters={"actor_role": "analyst"},
        status="SIMULATED_SUCCESS",
        executed_by="admin",
        actor_role="admin",
        authorization_decision="APPROVED",
        execution_log="[SIMULATION DRY RUN] Action 'BLOCK_IP' for target '45.154.255.89' simulated successfully. Zero destructive changes applied to perimeter infrastructure.",
        created_at=now
    ))

    # 8. Phase 3: Saved Threat Hunting Queries
    from backend.app.models.hunting import HuntingQuery
    db.add(HuntingQuery(
        name="High-Severity External Port Scanners",
        description="Identifies multi-port scanning vectors targeting production subnets in past 24h",
        query_definition={
            "entity": "alerts",
            "time_range": "24h",
            "filters": {"attack_type": "PortScan", "severity": "HIGH"}
        },
        created_by="admin",
        is_saved=True,
        created_at=now
    ))
    db.add(HuntingQuery(
        name="Tor & C2 Indicators Matching Ingress Traffic",
        description="Searches active C2 and Tor exit node indicators",
        query_definition={
            "entity": "iocs",
            "filters": {"ioc_type": "ipv4", "keyword": "185."}
        },
        created_by="analyst",
        is_saved=True,
        created_at=now
    ))

    # 9. Phase 3: Predictive Risk Forecasts
    from backend.app.models.predictive import RiskForecast, AlertVolumeForecast
    db.add(RiskForecast(
        asset_id=asset_objs["api-gateway"].id,
        forecast_type="24H",
        forecast_horizon="24_HOURS",
        predicted_score=87.5,
        confidence=0.89,
        baseline_score=65.0,
        model_family="phase3_predictive",
        model_version="forecast-v1",
        explanation={
            "status": "ACTIVE_TREND_FORECAST",
            "velocity_factor": 15.0,
            "outage_penalty": 7.5,
            "recent_alerts": 4,
            "recent_anomalies": 2
        },
        created_at=now
    ))
    db.add(AlertVolumeForecast(
        forecast_window="NEXT_24H",
        predicted_alert_count=42,
        confidence=0.86,
        model_family="phase3_predictive",
        model_version="volume-forecast-v1",
        historical_reference_count=36,
        created_at=now
    ))

    # 10. Phase 3: MITRE ATT&CK Matrix Coverage Snapshot
    from backend.app.models.attack_coverage import AttackCoverageSnapshot
    db.add(AttackCoverageSnapshot(
        observed_techniques_count=4,
        detected_techniques_count=4,
        total_matrix_techniques=26,
        coverage_percentage=15.4,
        tactic_breakdown={
            "Reconnaissance": {"total_techniques": 2, "detected_count": 1, "coverage_pct": 50.0, "is_active_observation": True},
            "Impact": {"total_techniques": 2, "detected_count": 1, "coverage_pct": 50.0, "is_active_observation": True},
            "Command and Control": {"total_techniques": 2, "detected_count": 1, "coverage_pct": 50.0, "is_active_observation": True},
            "Initial Access": {"total_techniques": 2, "detected_count": 1, "coverage_pct": 50.0, "is_active_observation": True}
        },
        technique_details={
            "detected_techniques": ["T1595 - Active Scanning", "T1498 - Network Denial of Service", "T1071 - Application Layer Protocol", "T1190 - Exploit Public-Facing App"]
        },
        created_at=now
    ))

    # 11. Phase 3: SOAR Response Approval Request
    from backend.app.models.response_approval import ResponseApproval
    db.add(ResponseApproval(
        incident_id=inc.id,
        requested_action="BLOCK_IOC_SIMULATION",
        target_entity="45.154.255.89",
        parameters={"firewall_profile": "edge-perimeter", "rule_action": "DROP"},
        requested_by="analyst",
        requested_at=now,
        status="REQUESTED",
        is_dry_run=True,
        reason="Correlated multi-alert DDoS vector confirmed with C2 threat intelligence feed match."
    ))

    await db.commit()
    logger.info("Successfully seeded Phase 1, Phase 2 & Phase 3 operational demo dataset.")
