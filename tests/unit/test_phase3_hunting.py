"""
tests/unit/test_phase3_hunting.py
=================================
Unit tests for Phase 3 Advanced Threat Hunting Query Engine.
"""

import pytest
from backend.app.database import AsyncSessionFactory
from backend.app.services.hunting_service import HuntingService
from backend.app.models.alert import Alert
from backend.app.models.protected_asset import ProtectedAsset
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_hunting_query_alerts_filtering():
    """Verify parameterized threat hunt filters alerts by severity, source IP, and attack type."""
    async with AsyncSessionFactory() as db:
        asset = ProtectedAsset(
            name="Hunt Test Target",
            hostname="hunt-target.corp",
            ip_address="198.51.100.99",
            asset_type="api",
            criticality="high"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        alert = Alert(
            asset_id=asset.id,
            title="Hunt Test DDoS Alert",
            source_ip="185.220.101.99",
            destination_ip="198.51.100.99",
            source_port=44444,
            destination_port=443,
            protocol="TCP",
            attack_type="DDoS_SYN_Flood",
            severity="CRITICAL",
            status="new",
            timestamp=datetime.now(timezone.utc)
        )
        db.add(alert)
        await db.commit()

        # Execute hunt
        query_def = {
            "entity": "alerts",
            "time_range": "24h",
            "filters": {
                "source_ip": "185.220.101.99",
                "severity": "CRITICAL",
                "attack_type": "DDoS"
            },
            "limit": 50
        }
        res = await HuntingService.execute_hunting_query(query_def, "test_hunter", None, db)
        assert res["result_count"] >= 1
        assert any(r["source_ip"] == "185.220.101.99" for r in res["results"])


@pytest.mark.asyncio
async def test_hunting_saved_query_lifecycle():
    """Verify creating and listing saved hunting templates."""
    async with AsyncSessionFactory() as db:
        q = await HuntingService.create_saved_query(
            name="Unit Test SSH Scanners",
            description="Testing template creation",
            query_definition={"entity": "alerts", "filters": {"attack_type": "SSH-Patator"}},
            created_by="analyst",
            db=db
        )
        assert q.id is not None

        saved_list = await HuntingService.list_saved_queries(db)
        assert any(sq.name == "Unit Test SSH Scanners" for sq in saved_list)
