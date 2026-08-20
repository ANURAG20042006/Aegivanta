"""
backend/app/observability/structured_logging.py
================================================
Phase 3.12 Observability: Structured JSON logging with request/trace context.
Implements a custom JSON formatter that enriches every log record with:
  - timestamp (ISO 8601 UTC)
  - service name
  - request_id
  - trace_id
  - event_type
  - severity
  - status

SECURITY: The sanitizer strips passwords, JWTs, API keys, tokens, and
secrets from log records before they are emitted.
"""

import json
import logging
import re
import threading
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Context variables — propagated across async tasks within the same request
# ---------------------------------------------------------------------------
_request_id_var: ContextVar[str] = ContextVar("request_id", default="")
_trace_id_var:   ContextVar[str] = ContextVar("trace_id",   default="")
_service_var:    ContextVar[str] = ContextVar("service",     default="SentinelAI")


def set_request_context(request_id: str = "", trace_id: str = "", service: str = "SentinelAI") -> None:
    """Sets request-scoped context variables for structured log enrichment."""
    _request_id_var.set(request_id or str(uuid.uuid4()))
    _trace_id_var.set(trace_id or "")
    _service_var.set(service)


def get_request_id() -> str:
    return _request_id_var.get()


def get_trace_id() -> str:
    return _trace_id_var.get()


# ---------------------------------------------------------------------------
# Sensitive field redaction
# ---------------------------------------------------------------------------
# Fields whose values are always fully redacted
_SENSITIVE_FIELD_NAMES = frozenset({
    "password", "passwd", "secret", "api_key", "apikey", "token",
    "jwt", "authorization", "auth", "credential", "private_key",
    "access_token", "refresh_token", "client_secret", "x_api_key",
    "x-api-key", "bearer"
})

# Regex patterns that indicate sensitive content even in unexpected fields
_SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"),  # JWT format
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # OpenAI-style API keys
    re.compile(r"ghp_[A-Za-z0-9]{36}"),  # GitHub PAT
]

_REDACTED = "[REDACTED]"


def _is_sensitive_key(key: str) -> bool:
    return key.lower().replace("-", "_") in _SENSITIVE_FIELD_NAMES


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        for pattern in _SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                return _REDACTED
    return value


def sanitize_log_record(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitizes a log record dict, redacting sensitive fields."""
    sanitized = {}
    for k, v in data.items():
        if _is_sensitive_key(str(k)):
            sanitized[k] = _REDACTED
        elif isinstance(v, dict):
            sanitized[k] = sanitize_log_record(v)
        elif isinstance(v, list):
            sanitized[k] = [
                sanitize_log_record(item) if isinstance(item, dict) else _redact_value(item)
                for item in v
            ]
        else:
            sanitized[k] = _redact_value(v)
    return sanitized


# ---------------------------------------------------------------------------
# JSON Log Formatter
# ---------------------------------------------------------------------------
class StructuredJSONFormatter(logging.Formatter):
    """
    Formats log records as structured JSON objects.
    Every record includes: timestamp, service, request_id, trace_id,
    event_type, severity, status, logger, and the original message.
    """

    SERVICE_NAME = "SentinelAI"

    def format(self, record: logging.LogRecord) -> str:
        # Resolve severity
        level = record.levelname.upper()
        severity = {
            "DEBUG":    "debug",
            "INFO":     "info",
            "WARNING":  "warning",
            "ERROR":    "error",
            "CRITICAL": "critical",
        }.get(level, "info")

        # Core structured fields
        log_entry: Dict[str, Any] = {
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "service":    _service_var.get() or self.SERVICE_NAME,
            "request_id": _request_id_var.get() or "",
            "trace_id":   _trace_id_var.get() or "",
            "event_type": getattr(record, "event_type", "log"),
            "severity":   severity,
            "status":     getattr(record, "status", ""),
            "logger":     record.name,
            "message":    record.getMessage(),
        }

        # Optional extra fields from log call
        for attr in ["event_type", "status", "component", "actor", "resource", "duration_ms"]:
            val = getattr(record, attr, None)
            if val is not None:
                log_entry[attr] = val

        # Exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Redact sensitive fields before emitting
        log_entry = sanitize_log_record(log_entry)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# Initialisation helper
# ---------------------------------------------------------------------------
def configure_structured_logging(level: str = "INFO", service_name: str = "SentinelAI") -> None:
    """
    Configures the root logger to emit structured JSON logs.
    Safe to call multiple times (idempotent).
    """
    root = logging.getLogger()
    # Avoid adding duplicate handlers
    for handler in root.handlers:
        if isinstance(handler.formatter, StructuredJSONFormatter):
            return  # Already configured

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJSONFormatter())
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    _service_var.set(service_name)
    logger = logging.getLogger("SentinelAI")
    logger.info("Structured JSON logging initialized", extra={"event_type": "system.init"})
