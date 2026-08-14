"""
backend/app/core/rate_limit.py
==============================
In-Memory Sliding Window Rate Limiting Dependency for Expensive SOC Analytics.
"""

import time
from collections import defaultdict
from fastapi import HTTPException, status, Request


class RateLimiter:
    """Sliding-window rate limiter per client IP / user identity."""

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.hits = defaultdict(list)

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window_start = now - 60.0

        # Filter out timestamps older than 60s
        self.hits[client_ip] = [t for t in self.hits[client_ip] if t > window_start]

        if len(self.hits[client_ip]) >= self.rpm:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: Max {self.rpm} requests per minute."
            )

        self.hits[client_ip].append(now)


# Pre-configured rate limiters
hunting_rate_limit = RateLimiter(requests_per_minute=45)
predictive_rate_limit = RateLimiter(requests_per_minute=60)
graph_rate_limit = RateLimiter(requests_per_minute=60)
