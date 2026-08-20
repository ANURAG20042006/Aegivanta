import gzip
import zlib
import json
import hashlib
import time
import logging
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.sensor import Sensor
from backend.app.services.usage_metering_service import UsageMeteringService
from backend.app.core.exceptions import SentinelAIException, AuthenticationError

logger = logging.getLogger("SentinelAI.TelemetryIngestion")

# Maximum decompressed payload size (10 MB)
MAX_DECOMPRESSED_BYTES = 10 * 1024 * 1024

SUPPORTED_SCHEMAS = {
    "NETWORK_FLOW",
    "AUTH_EVENT",
    "DNS_QUERY",
    "HTTP_METADATA",
    "PROCESS_EVENT",
    "SYSTEM_EVENT"
}


class TelemetryIngestionService:
    """High-performance compressed batch telemetry ingestion, deduplication & backpressure engine."""

    # In-memory LRU cache for event deduplication (stores last 50,000 event hashes)
    _dedup_cache: OrderedDict = OrderedDict()
    _dedup_max_size: int = 50000

    @classmethod
    def _is_duplicate(cls, event_hash: str) -> bool:
        """Checks if event hash exists in recent dedup cache; otherwise records it."""
        if event_hash in cls._dedup_cache:
            return True
        cls._dedup_cache[event_hash] = time.time()
        if len(cls._dedup_cache) > cls._dedup_max_size:
            cls._dedup_cache.popitem(last=False)
        return False

    @classmethod
    def decompress_payload(cls, raw_bytes: bytes, content_encoding: Optional[str] = None) -> Dict[str, Any]:
        """Decompresses gzip/zlib/deflate bytes or loads standard JSON with size limits."""
        if not raw_bytes:
            raise SentinelAIException(status_code=400, detail="Empty telemetry payload.")

        decompressed = raw_bytes
        encoding = (content_encoding or "").lower().strip()

        if encoding in ["gzip", "gz"] or raw_bytes.startswith(b"\x1f\x8b"):
            try:
                decompressed = gzip.decompress(raw_bytes)
            except Exception as e:
                raise SentinelAIException(status_code=400, detail=f"Gzip decompression failed: {str(e)}")
        elif encoding in ["deflate", "zlib"]:
            try:
                decompressed = zlib.decompress(raw_bytes)
            except Exception as e:
                raise SentinelAIException(status_code=400, detail=f"Deflate decompression failed: {str(e)}")

        if len(decompressed) > MAX_DECOMPRESSED_BYTES:
            raise SentinelAIException(
                status_code=413,
                detail=f"Decompressed payload size ({len(decompressed)} bytes) exceeds maximum limit of {MAX_DECOMPRESSED_BYTES} bytes."
            )

        try:
            return json.loads(decompressed.decode("utf-8"))
        except Exception as e:
            raise SentinelAIException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")

    @classmethod
    def validate_event(cls, event: Dict[str, Any], schema_version: str = "v1") -> Tuple[bool, Optional[str]]:
        """Validates schema conformance for supported telemetry types."""
        event_type = event.get("event_type", "").upper()
        if not event_type:
            return False, "Missing 'event_type' field."

        if event_type not in SUPPORTED_SCHEMAS:
            return False, f"Unsupported event_type '{event_type}'. Must be one of {list(SUPPORTED_SCHEMAS)}"

        data = event.get("data", {})
        if not isinstance(data, dict):
            return False, "Event 'data' payload must be a JSON object."

        if event_type == "NETWORK_FLOW":
            if not all(k in data for k in ["src_ip", "dst_ip", "src_port", "dst_port", "protocol"]):
                return False, "NETWORK_FLOW missing required 5-tuple fields (src_ip, dst_ip, src_port, dst_port, protocol)."
        elif event_type == "AUTH_EVENT":
            if not all(k in data for k in ["user", "src_ip", "success"]):
                return False, "AUTH_EVENT missing required fields (user, src_ip, success)."
        elif event_type == "DNS_QUERY":
            if not all(k in data for k in ["query_name", "query_type"]):
                return False, "DNS_QUERY missing required fields (query_name, query_type)."
        elif event_type == "HTTP_METADATA":
            if not all(k in data for k in ["method", "host", "uri", "status_code"]):
                return False, "HTTP_METADATA missing required fields (method, host, uri, status_code)."
        elif event_type == "PROCESS_EVENT":
            if not all(k in data for k in ["pid", "executable_path"]):
                return False, "PROCESS_EVENT missing required fields (pid, executable_path)."

        return True, None

    @classmethod
    async def process_telemetry_batch(
        cls,
        db: AsyncSession,
        sensor: Sensor,
        batch_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Processes a validated batch of telemetry events with deduplication and sequence sorting."""
        schema_version = batch_payload.get("schema_version", "v1")
        events: List[Dict[str, Any]] = batch_payload.get("events", [])

        if not events:
            return {"status": "SUCCESS", "events_processed": 0, "events_dropped": 0, "duplicates_suppressed": 0}

        # Sequence Sorting (order by seq_id if provided, else timestamp)
        events.sort(key=lambda x: (x.get("seq_id", 0), x.get("timestamp", "")))

        valid_events = []
        duplicates = 0
        dropped = 0

        for ev in events:
            # Validate schema
            is_valid, reason = cls.validate_event(ev, schema_version)
            if not is_valid:
                dropped += 1
                logger.warning("Dropped invalid telemetry event from sensor %s: %s", sensor.id, reason)
                continue

            # Deduplication
            ev_str = f"{sensor.id}:{ev.get('event_type')}:{json.dumps(ev.get('data', {}), sort_keys=True)}"
            ev_hash = hashlib.sha256(ev_str.encode("utf-8")).hexdigest()

            if cls._is_duplicate(ev_hash):
                duplicates += 1
                continue

            # Stamp with tenant and sensor metadata
            ev["tenant_id"] = sensor.tenant_id
            ev["sensor_id"] = sensor.id
            ev["ingested_at"] = datetime.now(timezone.utc).isoformat()
            valid_events.append(ev)

        # Usage Metering
        if valid_events:
            await UsageMeteringService.buffer_usage(
                tenant_id=sensor.tenant_id,
                metric_name="events_ingested",
                quantity=float(len(valid_events))
            )

        # Update Sensor Last Heartbeat & Offline Buffer Stats
        sensor.last_heartbeat = datetime.now(timezone.utc)
        sensor.offline_buffer_events = batch_payload.get("buffer_stats", {}).get("queued_events", 0)
        sensor.status = "ONLINE"
        await db.flush()

        return {
            "status": "SUCCESS",
            "sensor_id": sensor.id,
            "tenant_id": sensor.tenant_id,
            "events_processed": len(valid_events),
            "events_dropped": dropped,
            "duplicates_suppressed": duplicates,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
