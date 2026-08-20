"""
tests/unit/test_phase48_rate_limiting.py
========================================
Phase 4.8 Tenant-Aware Rate Limiting Tests.
Validates sliding-window enforcement, HTTP 429 exceptions, and quota headers.
"""

import pytest
import time
from backend.app.core.tenant_rate_limiter import TenantRateLimiter
from backend.app.core.exceptions import SentinelAIException


class TestTenantRateLimiting:

    def test_rate_limiter_permits_within_limit(self):
        """Rate limiter must permit requests when volume is within configured threshold."""
        limiter = TenantRateLimiter(default_rpm=5)
        for i in range(5):
            allowed, remaining = limiter.check("tenant-test", max_requests=5, window_seconds=60)
            assert allowed is True
            assert remaining == (4 - i)

    def test_rate_limiter_denies_exceeding_limit(self):
        """Rate limiter must return allowed=False when limit is exhausted."""
        limiter = TenantRateLimiter(default_rpm=3)
        for _ in range(3):
            limiter.check("tenant-exhaust", max_requests=3, window_seconds=60)

        # 4th request must be denied
        allowed, remaining = limiter.check("tenant-exhaust", max_requests=3, window_seconds=60)
        assert allowed is False
        assert remaining == 0

    def test_enforce_raises_429_with_headers(self):
        """enforce() must raise SentinelAIException with status 429 and Retry-After header."""
        limiter = TenantRateLimiter(default_rpm=2)
        limiter.enforce("tenant-429", max_requests=2, window_seconds=60)
        limiter.enforce("tenant-429", max_requests=2, window_seconds=60)

        with pytest.raises(SentinelAIException) as excinfo:
            limiter.enforce("tenant-429", max_requests=2, window_seconds=60)

        assert excinfo.value.status_code == 429
        assert "Retry-After" in excinfo.value.headers
        assert excinfo.value.headers["Retry-After"] == "60"
