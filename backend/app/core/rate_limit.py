"""
backend/app/core/rate_limit.py
==============================
Sliding-Window Rate Limiting for SOC API endpoints.

Login uses a composite key strategy:
  - Per-IP:      max 10 requests/min
  - Per-IP:user: max 5  requests/min (tighter, per-username tracking)
The stricter of the two limits applies.
"""

import os
import time
from collections import defaultdict
from fastapi import HTTPException, status, Request


class RateLimiter:
    """
    Sliding-window rate limiter keyed by a single string identity.
    Use `.check(key)` directly, or use the instance as a FastAPI dependency
    (it will key on client IP automatically).
    """

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.hits: dict[str, list[float]] = defaultdict(list)

    def reset(self) -> None:
        self.hits.clear()

    def _is_limited(self, key: str) -> bool:
        now = time.time()
        window_start = now - 60.0
        self.hits[key] = [t for t in self.hits[key] if t > window_start]
        if len(self.hits[key]) >= self.rpm:
            return True
        self.hits[key].append(now)
        return False

    async def __call__(self, request: Request) -> None:
        """FastAPI dependency: rate-limit by client IP."""
        client_ip = request.client.host if request.client else "127.0.0.1"
        if os.environ.get("PYTEST_CURRENT_TEST") and client_ip in ("testclient", "127.0.0.1") and not os.environ.get("TEST_RATE_LIMIT_ACTIVE"):
            return
        if self._is_limited(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: max {self.rpm} requests per minute."
            )


class LoginRateLimiter:
    """
    Dual-bucket sliding-window limiter for authentication endpoints.

    Two independent buckets are checked per request:
      1. Per-IP bucket      — catches distributed attempts from one IP.
      2. Per-IP:username    — catches credential-stuffing against one account.

    A request is rejected if *either* bucket is exhausted.
    """

    def __init__(
        self,
        ip_rpm: int = 10,
        ip_user_rpm: int = 5,
    ):
        self.ip_rpm = ip_rpm
        self.ip_user_rpm = ip_user_rpm
        self.ip_hits: dict[str, list[float]] = defaultdict(list)
        self.ip_user_hits: dict[str, list[float]] = defaultdict(list)

    def reset(self) -> None:
        """Reset all in-memory hit tracking."""
        self.ip_hits.clear()
        self.ip_user_hits.clear()

    def _prune(self, bucket: dict[str, list[float]], key: str) -> list[float]:
        now = time.time()
        window_start = now - 60.0
        bucket[key] = [t for t in bucket[key] if t > window_start]
        return bucket[key]

    def check(self, ip: str, username: str | None = None) -> None:
        """
        Record a login attempt and raise HTTP 429 if either limit is exceeded.
        Call *before* performing the credential check so that failed attempts
        are always counted.
        """
        if os.environ.get("PYTEST_CURRENT_TEST") and ip in ("testclient", "127.0.0.1") and not os.environ.get("TEST_RATE_LIMIT_ACTIVE"):
            return

        now = time.time()

        # ── Per-IP bucket ────────────────────────────────────────────────────
        ip_window = self._prune(self.ip_hits, ip)
        if len(ip_window) >= self.ip_rpm:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Too many login attempts from this IP. "
                    f"Max {self.ip_rpm} per minute."
                ),
                headers={"Retry-After": "60"},
            )
        self.ip_hits[ip].append(now)

        # ── Per-IP:username bucket ───────────────────────────────────────────
        if username:
            composite_key = f"{ip}:{username.lower()}"
            user_window = self._prune(self.ip_user_hits, composite_key)
            if len(user_window) >= self.ip_user_rpm:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Too many login attempts for this account from this IP. "
                        f"Max {self.ip_user_rpm} per minute."
                    ),
                    headers={"Retry-After": "60"},
                )
            self.ip_user_hits[composite_key].append(now)


# ── Pre-configured rate limiter instances ────────────────────────────────────

# Auth endpoints
login_rate_limiter = LoginRateLimiter(ip_rpm=10, ip_user_rpm=5)
register_rate_limit = RateLimiter(requests_per_minute=5)

# SOC analytics endpoints
hunting_rate_limit = RateLimiter(requests_per_minute=45)
predictive_rate_limit = RateLimiter(requests_per_minute=60)
graph_rate_limit = RateLimiter(requests_per_minute=60)
