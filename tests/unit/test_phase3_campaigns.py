"""
tests/unit/test_phase3_campaigns.py
===================================
Unit tests for Multi-Incident Campaign Correlation Engine.
"""

import pytest
from backend.app.database import AsyncSessionFactory
from backend.app.services.campaign_service import CampaignService
from backend.app.models.incident import Incident
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_campaign_clustering_by_subnet():
    """Verify multiple incidents from same subnet are clustered into a campaign without fabricated attribution."""
    async with AsyncSessionFactory() as db:
        now = datetime.now(timezone.utc)
        inc1 = Incident(
            incident_code="INC-CAMP-01",
            source_ip="198.51.100.5",
            destination_ip="10.0.0.1",
            source_port=50001,
            destination_port=80,
            protocol="TCP",
            packet_length=512,
            is_malicious=True,
            attack_type="DDoS",
            severity="High",
            risk_score=80.0,
            timestamp=now
        )
        inc2 = Incident(
            incident_code="INC-CAMP-02",
            source_ip="198.51.100.9",
            destination_ip="10.0.0.2",
            source_port=50002,
            destination_port=80,
            protocol="TCP",
            packet_length=512,
            is_malicious=True,
            attack_type="DDoS",
            severity="High",
            risk_score=85.0,
            timestamp=now
        )
        db.add(inc1)
        db.add(inc2)
        await db.commit()

        campaigns = await CampaignService.detect_campaigns(lookback_hours=24, db=db)
        assert len(campaigns) >= 1
        
        # Verify attribution safety invariant
        for camp in campaigns:
            assert "attribution" in camp
            assert "UNKNOWN" in camp["attribution"]
            assert camp["confidence_label"] in ["CORRELATED_CAMPAIGN", "POSSIBLE_CAMPAIGN"]
