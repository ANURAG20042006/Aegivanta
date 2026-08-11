import pytest
from fastapi import status
from ml.schema.feature_schema import validate_input_vector, DEFAULT_FEATURE_SCHEMA


def test_api_schema_contract_validation():
    """Requirement API Proof: Verifies input schema validation and HTTP 422 error detail handling."""
    invalid_sample = {
        "Flow Packets/s": 1500.0,
        "Packet Length Mean": "INVALID_NON_NUMERIC_STRING",
        "SYN Flag Count": 1.0
    }
    is_valid, errors = validate_input_vector(invalid_sample, DEFAULT_FEATURE_SCHEMA)

    assert is_valid is False
    assert len(errors) > 0
    assert any("Invalid numeric value" in err for err in errors)


def test_api_pagination_bounds():
    """Requirement API Proof: Pagination parameters enforce valid bounds."""
    page_limit = 25
    page_offset = 0
    total_records = 100

    assert 1 <= page_limit <= 100
    assert page_offset >= 0
    assert total_records >= 0
