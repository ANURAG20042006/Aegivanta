"""
tests/unit/test_threat_hunting_service.py
=========================================
Phase 3.8 Unit Tests: Threat Hunting Query DSL & Validator.
"""

import pytest
from backend.app.services.threat_hunting_service import ThreatHuntingService, ThreatHuntingQueryValidator


@pytest.mark.unit
def test_query_validator_allowed_and_disallowed_fields():
    """Verify query validator enforces field whitelisting."""
    # Valid field
    ThreatHuntingQueryValidator.validate_filter("source_ip", "equals", "10.0.0.1")
    ThreatHuntingQueryValidator.validate_filter("destination_port", "equals", 445)
    ThreatHuntingQueryValidator.validate_filter("severity", "in", ["HIGH", "CRITICAL"])

    # Disallowed field
    with pytest.raises(ValueError, match="not a permitted threat hunting query field"):
        ThreatHuntingQueryValidator.validate_filter("unauthorized_internal_table", "equals", "val")


@pytest.mark.unit
def test_query_validator_sql_injection_defense():
    """Verify query validator rejects SQL injection in field names and operators."""
    with pytest.raises(ValueError, match="not a permitted threat hunting query field"):
        ThreatHuntingQueryValidator.validate_filter("source_ip; DROP TABLE users;--", "equals", "10.0.0.1")

    with pytest.raises(ValueError, match="Operator 'UNION SELECT' is not supported"):
        ThreatHuntingQueryValidator.validate_filter("source_ip", "UNION SELECT", "10.0.0.1")


@pytest.mark.unit
def test_query_validator_invalid_operator():
    """Verify query validator rejects unsupported operators."""
    with pytest.raises(ValueError, match="Operator 'regex_match' is not supported"):
        ThreatHuntingQueryValidator.validate_filter("source_ip", "regex_match", ".*")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_dsl_query_structure_and_limits():
    """Verify DSL query executes and bounds limits."""
    res = await ThreatHuntingService.execute_dsl_query(
        entity="events",
        filters=[{"field": "source_ip", "operator": "equals", "value": "192.168.1.50"}],
        limit=2000,  # Clamped to max 1000
        offset=0
    )
    assert res["entity"] == "events"
    assert res["limit"] == 1000
    assert "duration_ms" in res
    assert isinstance(res["results"], list)
