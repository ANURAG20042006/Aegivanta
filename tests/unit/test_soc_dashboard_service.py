"""
tests/unit/test_soc_dashboard_service.py
========================================
Unit tests for SOCDashboardService: Overview metrics, Incident search & pagination,
Detections distribution, Threat Intel stats, SOAR Response status, Investigations,
MITRE coverage, System Health, and Events stream.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import AsyncSessionFactory, init_db
from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.threat_intel import ThreatIndicator, ThreatFeed
from backend.app.models.investigation import InvestigationCase
from backend.app.models.response import ResponseActionRecord
from backend.app.services.soc_dashboard_service import SOCDashboardService
from backend.app.services.soc_event_broadcaster import broadcast_soc_event


@pytest.mark.asyncio
async def test_dashboard_overview_metrics_calculation():
    await init_db()
    async with AsyncSessionFactory() as db:
        metrics = await SOCDashboardService.get_overview_metrics(db=db, lookback_days=30)

        assert "total_incidents" in metrics
        assert "open_incidents" in metrics
        assert "critical_incidents" in metrics
        assert "mean_time_to_detect_minutes" in metrics
        assert "mean_time_to_acknowledge_minutes" in metrics
        assert "mean_time_to_respond_minutes" in metrics
        assert "mean_time_to_resolve_minutes" in metrics
        assert "active_investigations" in metrics
        assert "active_soar_actions" in metrics
        assert "detection_rate_per_hour" in metrics
        assert "false_positive_rate_pct" in metrics
        assert "event_ingestion_rate_eps" in metrics
        assert "mitre_coverage_pct" in metrics
        assert "attack_graph_nodes" in metrics
        assert metrics["system_status"] in ["HEALTHY", "DEGRADED"]


@pytest.mark.asyncio
async def test_dashboard_incidents_filtering_and_pagination():
    await init_db()
    async with AsyncSessionFactory() as db:
        # Seed test asset and incident
        asset = ProtectedAsset(
            name="SOC Command Server",
            hostname="soc-srv-01.internal",
            ip_address="10.0.99.10",
            criticality="critical",
            environment="production"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        inc = Incident(
            incident_code="INC-DASH-001",
            title="DDoS Dashboard Test Incident",
            description="Testing dashboard query engine",
            severity="Critical",
            risk_score=95,
            status="OPEN",
            source_ip="198.51.100.42",
            destination_ip="10.0.99.10",
            source_port=44212,
            destination_port=80,
            protocol="TCP",
            packet_length=512,
            attack_type="DDoS",
            confidence_score=0.98,
            is_malicious=True,
            asset_id=asset.id,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(inc)
        await db.commit()

        # Query page 1
        res = await SOCDashboardService.get_dashboard_incidents(
            db=db,
            page=1,
            limit=10,
            search="INC-DASH-001"
        )

        assert res["total"] >= 1
        assert len(res["items"]) >= 1
        found = next(i for i in res["items"] if i["incident_code"] == "INC-DASH-001")
        assert found["asset_name"] == "SOC Command Server"
        assert found["asset_criticality"] == "CRITICAL"
        assert found["severity"] == "Critical"
        assert found["risk_score"] == 95


@pytest.mark.asyncio
async def test_dashboard_detections_aggregation():
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SOCDashboardService.get_dashboard_detections(db=db, lookback_days=30)
        assert "total_detections" in res
        assert "severity_breakdown" in res
        assert "attack_type_distribution" in res
        assert "recent_detections" in res


@pytest.mark.asyncio
async def test_dashboard_threat_intel_aggregation():
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SOCDashboardService.get_dashboard_threat_intel(db=db)
        assert "active_indicators_count" in res
        assert "total_feeds" in res
        assert "cache_stats" in res


@pytest.mark.asyncio
async def test_dashboard_response_aggregation():
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SOCDashboardService.get_dashboard_response(db=db)
        assert "pending_approvals_count" in res
        assert "executing_actions_count" in res
        assert "successful_actions_count" in res
        assert "average_response_latency_ms" in res


@pytest.mark.asyncio
async def test_dashboard_investigations_aggregation():
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SOCDashboardService.get_dashboard_investigations(db=db)
        assert "total_investigations" in res
        assert "open_investigations" in res
        assert "status_breakdown" in res
        assert "priority_breakdown" in res


@pytest.mark.asyncio
async def test_dashboard_mitre_aggregation():
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SOCDashboardService.get_dashboard_mitre(db=db)
        assert "total_catalog_techniques" in res
        assert "covered_techniques_count" in res
        assert "coverage_percentage" in res


@pytest.mark.asyncio
async def test_dashboard_system_health_aggregation():
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SOCDashboardService.get_dashboard_system_health(db=db)
        assert res["overall_status"] in ["HEALTHY", "DEGRADED"]
        assert "components" in res
        comps = res["components"]
        assert "api" in comps
        assert "postgresql" in comps
        assert "redis" in comps
        assert "ml_inference" in comps
        assert "workers" in comps
        assert "websockets" in comps
        # Zero secret exposure check
        raw_dump = str(res).lower()
        assert "password" not in raw_dump
        assert "secret_key" not in raw_dump


@pytest.mark.asyncio
async def test_dashboard_events_retrieval():
    await broadcast_soc_event(
        event_type="SYSTEM_ALERT",
        title="Command Center Initialized",
        description="SOC Command Center event pipeline active",
        severity="INFO"
    )
    events = SOCDashboardService.get_dashboard_events(limit=5)
    assert len(events) >= 1
    assert any(e["title"] == "Command Center Initialized" for e in events)
