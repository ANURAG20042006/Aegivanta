import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.app.core.logging import logger


class RequestTimingAndAuditMiddleware(BaseHTTPMiddleware):
    """Middleware for recording request execution latency and logging access details."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url_path = request.url.path

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000  # milliseconds
            response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

            # Log request telemetry
            logger.info(
                f"[{method}] {url_path} - Status: {response.status_code} - "
                f"Client: {client_ip} - Duration: {process_time:.2f}ms"
            )
            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"[{method}] {url_path} FAILED - Client: {client_ip} - "
                f"Duration: {process_time:.2f}ms - Exception: {str(exc)}"
            )
            raise exc
