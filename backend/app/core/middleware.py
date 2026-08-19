import time
import uuid
import re
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.app.core.logging import logger


class RequestTimingAndAuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for recording request execution latency, enforcing correlation request IDs (X-Request-ID),
    and logging audit telemetry.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url_path = request.url.path

        # Correlation Request ID Handling (Requirement 3.16)
        raw_request_id = request.headers.get("X-Request-ID", "").strip()
        if raw_request_id and len(raw_request_id) <= 64 and re.match(r"^[a-zA-Z0-9_\-]+$", raw_request_id):
            request_id = raw_request_id
        else:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000.0  # milliseconds
            response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
            response.headers["X-Request-ID"] = request_id
            
            # Security Hardening Response Headers (Phase 2 Step 6)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

            # Log request telemetry with correlation request_id
            logger.info(
                f"[{method}] {url_path} - Status: {response.status_code} - "
                f"Client: {client_ip} - Duration: {process_time:.2f}ms - RequestID: {request_id}"
            )
            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000.0
            logger.error(
                f"[{method}] {url_path} FAILED - Client: {client_ip} - "
                f"Duration: {process_time:.2f}ms - RequestID: {request_id} - Exception: {str(exc)}"
            )
            raise exc
