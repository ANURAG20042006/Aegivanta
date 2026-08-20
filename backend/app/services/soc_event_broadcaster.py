"""
backend/app/services/soc_event_broadcaster.py
=============================================
Production Real-Time SOC Event Stream Engine.
Coordinates real-time SOC operational events across WebSockets, Redis Pub/Sub,
in-memory ring buffer, deduplication gates, and sequence ordering.
"""

from datetime import datetime, timezone
import uuid
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Set
from collections import deque

from backend.app.config import settings

logger = logging.getLogger("SentinelAI")

# Supported canonical SOC event types (12 categories)
SOC_EVENT_TYPES = {
    "NEW_DETECTION": "New threat detection rule trigger or ML anomaly",
    "NEW_INCIDENT": "New security incident created or correlated",
    "INCIDENT_SEVERITY_ESCALATION": "Incident severity or risk score escalated",
    "INCIDENT_STATUS_CHANGE": "Incident workflow state transitioned",
    "THREAT_INTEL_MATCH": "Threat intelligence IOC hit on live traffic",
    "LATERAL_MOVEMENT_DETECTION": "Multi-hop lateral movement trajectory detected",
    "RESPONSE_ACTION_REQUESTED": "Autonomous or manual response action requested",
    "RESPONSE_ACTION_APPROVED": "Response action approved by authorized analyst/admin",
    "RESPONSE_ACTION_EXECUTED": "Response remediation action executed",
    "RESPONSE_ROLLBACK": "Remediation action rolled back",
    "INVESTIGATION_UPDATE": "Investigation case created, note added, or status changed",
    "SYSTEM_ALERT": "System health or infrastructure alert"
}

VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}


class SOCEventBroadcaster:
    """
    Singleton broadcaster managing real-time SOC event publication,
    in-memory ring buffer, deduplication, and multi-node stream synchronization.
    """

    def __init__(self, max_buffer_size: int = 250):
        self._max_buffer_size = max_buffer_size
        self._event_buffer: deque = deque(maxlen=max_buffer_size)
        self._seen_event_ids: deque = deque(maxlen=1000)
        self._seen_event_set: Set[str] = set()
        self._sequence_counter: int = 0
        self._lock = asyncio.Lock()

    @property
    def buffer_size(self) -> int:
        return len(self._event_buffer)

    @property
    def total_events_published(self) -> int:
        return self._sequence_counter

    def is_duplicate(self, event_id: str) -> bool:
        """O(1) duplicate check for distributed events."""
        return event_id in self._seen_event_set

    def record_event_id(self, event_id: str) -> None:
        """Records event_id to deduplication cache with bounded memory."""
        if len(self._seen_event_ids) >= 1000:
            oldest = self._seen_event_ids.popleft()
            self._seen_event_set.discard(oldest)
        self._seen_event_ids.append(event_id)
        self._seen_event_set.add(event_id)

    async def broadcast_event(
        self,
        event_type: str,
        title: str,
        description: str,
        severity: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
        publish_to_redis: bool = True
    ) -> Dict[str, Any]:
        """
        Creates, buffers, and broadcasts a structured SOC event to all
        connected WebSocket clients and the Redis Pub/Sub cluster backplane.
        """
        evt_id = event_id or str(uuid.uuid4())
        norm_type = event_type.upper().strip()
        if norm_type not in SOC_EVENT_TYPES:
            # Fallback or allow extension
            norm_type = norm_type

        norm_sev = severity.upper().strip() if severity else "INFO"
        if norm_sev not in VALID_SEVERITIES:
            norm_sev = "INFO"

        if self.is_duplicate(evt_id):
            logger.debug("Suppressed duplicate SOC event: %s", evt_id)
            return {"event_id": evt_id, "status": "DUPLICATE_SUPPRESSED"}

        self.record_event_id(evt_id)

        now_utc = datetime.now(timezone.utc)
        self._sequence_counter += 1

        event_payload = {
            "event_id": evt_id,
            "sequence": self._sequence_counter,
            "type": norm_type,
            "severity": norm_sev,
            "title": title,
            "description": description,
            "timestamp": now_utc.isoformat(),
            "epoch_ms": int(now_utc.timestamp() * 1000),
            "metadata": metadata or {}
        }

        # Store in circular ring buffer
        self._event_buffer.append(event_payload)

        # 1. Broadcast locally to all WebSocket clients
        try:
            from backend.app.api.v1.websockets import manager
            await manager.broadcast_event(
                event_type=norm_type,
                data=event_payload,
                publish_to_redis=False  # Handled below
            )
        except Exception as ws_err:
            logger.debug("Local WebSocket broadcast error: %s", ws_err)

        # 2. Publish across Redis Pub/Sub backplane
        if publish_to_redis:
            try:
                from backend.app.services.distributed_stream_service import distributed_stream_engine
                await distributed_stream_engine.backend.publish_pubsub(
                    f"{settings.STREAM_PUBSUB_CHANNEL}:soc_events",
                    event_payload
                )
            except Exception as pub_err:
                logger.debug("Redis Pub/Sub broadcast notice: %s", pub_err)

        return event_payload

    def get_recent_events(
        self,
        limit: int = 50,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        since_iso: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves recent events from in-memory ring buffer with optional filtering,
        ordered by sequence descending (newest first).
        """
        events = list(self._event_buffer)
        events.reverse()  # Newest first

        filtered = []
        for evt in events:
            if event_type and evt.get("type") != event_type.upper():
                continue
            if severity and evt.get("severity") != severity.upper():
                continue
            if since_iso:
                try:
                    since_dt = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
                    evt_dt = datetime.fromisoformat(evt["timestamp"].replace("Z", "+00:00"))
                    if evt_dt < since_dt:
                        continue
                except Exception:
                    pass
            filtered.append(evt)
            if len(filtered) >= limit:
                break

        return filtered

    def clear_buffer(self) -> None:
        """Clears in-memory buffer (for testing)."""
        self._event_buffer.clear()
        self._seen_event_ids.clear()
        self._seen_event_set.clear()
        self._sequence_counter = 0


# Global Singleton Event Broadcaster
soc_broadcaster = SOCEventBroadcaster()


async def broadcast_soc_event(
    event_type: str,
    title: str,
    description: str,
    severity: str = "INFO",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience helper to broadcast a SOC event anywhere in the codebase."""
    return await soc_broadcaster.broadcast_event(
        event_type=event_type,
        title=title,
        description=description,
        severity=severity,
        metadata=metadata
    )
