import time
import threading
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status
from backend.app.core.exceptions import SentinelAIException


class TenantRateLimiter:
    """
    Sliding window in-memory rate limiter per tenant, user, or API key.
    Provides sub-millisecond enforcement with automatic window pruning.
    """

    def __init__(self, default_rpm: int = 120):
        self.default_rpm = default_rpm
        self._windows: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, max_requests: int = 0, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Evaluates sliding window request count for key.
        Returns (is_allowed, remaining_quota).
        """
        limit = max_requests if max_requests > 0 else self.default_rpm
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            timestamps = self._windows.get(key, [])
            # Prune expired timestamps
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= limit:
                self._windows[key] = timestamps
                return False, 0

            timestamps.append(now)
            self._windows[key] = timestamps
            remaining = max(0, limit - len(timestamps))
            return True, remaining

    def enforce(self, key: str, max_requests: int = 0, window_seconds: int = 60) -> None:
        """Enforces rate limit, raising HTTP 429 Too Many Requests on breach."""
        allowed, remaining = self.check(key, max_requests, window_seconds)
        if not allowed:
            raise SentinelAIException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for identifier '{key}'. Please retry after window resets.",
                headers={"Retry-After": str(window_seconds), "X-RateLimit-Remaining": "0"}
            )


# Global Tenant Rate Limiter Instance
tenant_rate_limiter = TenantRateLimiter(default_rpm=300)
api_key_rate_limiter = TenantRateLimiter(default_rpm=120)
telemetry_rate_limiter = TenantRateLimiter(default_rpm=1000)
