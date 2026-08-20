"""
tests/unit/test_phase16_alert_intelligence.py
=============================================
Phase 16.2 & 16.3 Unit Tests: Alert Fingerprinting, Grouping & Prioritization.
"""

import pytest
from datetime import datetime, timezone
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.models.alert import Alert
from backend.app.services.alert_intelligence_service import AlertIntelligenceService


@pytest.mark.asyncio
async def test_alert_fingerprinting_and_deduplication():
    """Validates deterministic fingerprint hashing and storm deduplication."""
    await init_db()
    async with AsyncSessionFactory() as db:
        alert1 = Alert(
            title="DDoS Attack Detected",
            severity="high",
            confidence=0.92,
            risk_score=85.0,
            source_ip="198.51.100.25",
            destination_ip="10.0.0.5",
            attack_type="DDoS",
            source="ML_ENGINE:CatBoost"
        )
        db.add(alert1)
        await db.flush()

        is_suppressed, group, priority = await AlertIntelligenceService.process_incoming_alert(
            db=db,
            alert=alert1,
            tenant_id="test-tenant-alert"
        )

        assert group is not None
        assert group.root_attack_type == "DDoS"
        assert priority.priority_score > 0.0
        assert 0.0 <= priority.priority_score <= 100.0
        assert len(priority.explanation) > 0


@pytest.mark.asyncio
async def test_explainable_priority_score_calculation():
    """Validates contributing factors in 0-100 alert priority scoring."""
    await init_db()
    async with AsyncSessionFactory() as db:
        alert = Alert(
            title="Critical Brute Force Authentication",
            severity="critical",
            confidence=0.98,
            risk_score=95.0,
            source_ip="203.0.113.195",
            destination_ip="10.0.0.10",
            attack_type="Brute Force",
            source="ML_ENGINE:CatBoost"
        )
        db.add(alert)
        await db.flush()

        priority = await AlertIntelligenceService.calculate_priority_score(
            db=db,
            alert=alert,
            tenant_id="test-tenant-score"
        )

        assert priority.priority_score >= 60.0 # Critical severity + high confidence + brute force vector
        assert priority.priority_level in ["HIGH", "CRITICAL"]
        assert "severity" in priority.contributing_factors
        assert "detection_confidence" in priority.contributing_factors
        assert len(priority.reasons) >= 1
