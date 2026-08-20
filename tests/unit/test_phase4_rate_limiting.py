"""
tests/unit/test_phase4_rate_limiting.py
=======================================
Unit tests for Phase 4 Tenant-Aware Sliding Window Rate Limiter.
"""

import pytest
from backend.app.core.tenant_rate_limiter import TenantRateLimiter
from backend.app.core.exceptions import SentinelAIException


def test_sliding_window_rate_limiter_recovery():
    """Validates quota recovery after window expiration."""
    limiter = TenantRateLimiter(default_rpm=2)
    allowed1, rem1 = limiter.check("client-recovery", max_requests=2, window_seconds=1)
    allowed2, rem2 = limiter.check("client-recovery", max_requests=2, window_seconds=1)
    allowed3, rem3 = limiter.check("client-recovery", max_requests=2, window_seconds=1)

    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is False
