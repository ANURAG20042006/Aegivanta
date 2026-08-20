"""
backend/app/services/stream_consumer_base.py
============================================
Phase 3.11 Horizontal Scaling: Base consumer with consumer groups,
XAUTOCLAIM-based orphan recovery, backpressure, and dead-letter queuing.
Each worker role subclasses this and overrides process_event().
"""

import asyncio
import json
import logging
import os
import socket
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.services.worker_registry import (
    WorkerRole,
    WORKER_STREAM_ASSIGNMENTS,
    WORKER_RETRY_POLICY,
    BACKPRESSURE_THRESHOLDS,
    get_consumer_group,
)

logger = logging.getLogger("SentinelAI")

# Milliseconds before a pending message is considered abandoned and claimable
CLAIM_IDLE_MS = 60_000  # 60 seconds
CLAIM_BATCH   = 20


class StreamConsumerBase(ABC):
    """
    Base class for all SentinelAI horizontally-scalable stream consumers.

    Lifecycle:
      1. Connect to Redis
      2. Ensure consumer groups exist (XGROUP CREATE MKSTREAM)
      3. Loop: read → process → ack || retry/dlq
      4. Periodically claim orphaned PEL messages (XAUTOCLAIM)

    Subclasses must implement:
      - process_event(stream_key, event_data) → bool
    """

    def __init__(self, role: WorkerRole, redis_client=None):
        self.role = role
        self.redis = redis_client
        self.consumer_group = get_consumer_group(role)
        # Unique consumer name per pod/process
        self.consumer_name = f"{role.value}-{socket.gethostname()}-{os.getpid()}"
        self.streams = WORKER_STREAM_ASSIGNMENTS[role]
        self.retry_policy = WORKER_RETRY_POLICY[role]
        self.backpressure_threshold = BACKPRESSURE_THRESHOLDS[role]
        self._running = False
        self._retry_counts: Dict[str, int] = {}  # msg_id → retry_count

    # ------------------------------------------------------------------ #
    #  Abstract interface                                                  #
    # ------------------------------------------------------------------ #
    @abstractmethod
    async def process_event(self, stream_key: str, event_data: Dict[str, Any]) -> bool:
        """
        Process a single event from the given stream.
        Returns True on success, False to trigger retry.
        Raise an exception to also trigger retry with logging.
        """

    # ------------------------------------------------------------------ #
    #  Consumer group bootstrap                                           #
    # ------------------------------------------------------------------ #
    async def _ensure_consumer_groups(self) -> None:
        """Creates consumer groups for each assigned stream if they don't exist."""
        if not self.redis:
            return
        for stream_key in self.streams:
            if stream_key.startswith("sentinelai:dl_queue:"):
                continue  # DLQ streams are read-only by this consumer
            try:
                await self.redis.xgroup_create(
                    stream_key,
                    self.consumer_group,
                    id="0",
                    mkstream=True
                )
                logger.info("[%s] Consumer group '%s' created on '%s'",
                            self.role.value, self.consumer_group, stream_key)
            except Exception as e:
                # BUSYGROUP = already exists, safe to ignore
                if "BUSYGROUP" in str(e):
                    logger.debug("[%s] Consumer group '%s' already exists on '%s'",
                                 self.role.value, self.consumer_group, stream_key)
                else:
                    logger.warning("[%s] Could not create consumer group on '%s': %s",
                                   self.role.value, stream_key, e)

    # ------------------------------------------------------------------ #
    #  Backpressure check                                                 #
    # ------------------------------------------------------------------ #
    async def _is_backpressured(self, stream_key: str) -> bool:
        """Checks if the PEL size for this consumer group exceeds threshold."""
        if not self.redis:
            return False
        try:
            info = await self.redis.xpending(stream_key, self.consumer_group)
            pending_count = info.get("pending", 0) if isinstance(info, dict) else 0
            if pending_count > self.backpressure_threshold:
                logger.warning("[%s] Backpressure: %d pending > %d on '%s', pausing",
                               self.role.value, pending_count, self.backpressure_threshold, stream_key)
                return True
        except Exception:
            pass
        return False

    # ------------------------------------------------------------------ #
    #  Orphan recovery via XAUTOCLAIM                                     #
    # ------------------------------------------------------------------ #
    async def _claim_orphaned_messages(self, stream_key: str) -> List[Dict[str, Any]]:
        """Claims messages idle > CLAIM_IDLE_MS from other consumers in the group."""
        if not self.redis:
            return []
        try:
            result = await self.redis.xautoclaim(
                stream_key,
                self.consumer_group,
                self.consumer_name,
                CLAIM_IDLE_MS,
                "0-0",
                count=CLAIM_BATCH
            )
            # result is (next_start_id, messages, deleted_ids) in redis-py >= 4.3
            if result and len(result) >= 2:
                messages = result[1]
                if messages:
                    logger.info("[%s] Claimed %d orphaned messages from '%s'",
                                self.role.value, len(messages), stream_key)
                return messages or []
        except Exception as e:
            if "ERR" not in str(e):
                logger.debug("[%s] XAUTOCLAIM skipped (%s): %s", self.role.value, stream_key, e)
        return []

    # ------------------------------------------------------------------ #
    #  Dead-letter queue                                                  #
    # ------------------------------------------------------------------ #
    async def _send_to_dlq(self, stream_key: str, msg_id: str, event_data: Dict[str, Any], reason: str) -> None:
        """Publishes a failed message to the DLQ stream for forensic review."""
        dlq_key = f"sentinelai:dl_queue:{self.role.value}"
        if not self.redis:
            logger.error("[%s] DLQ: no Redis client; dropping msg_id=%s reason=%s", self.role.value, msg_id, reason)
            return
        try:
            payload = {
                "original_stream": stream_key,
                "original_msg_id": msg_id,
                "consumer_group": self.consumer_group,
                "consumer_name": self.consumer_name,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload_json": json.dumps(event_data, default=str)[:4096]
            }
            await self.redis.xadd(dlq_key, payload, maxlen=10_000, approximate=True)
            logger.warning("[%s] Message %s moved to DLQ '%s': %s",
                           self.role.value, msg_id, dlq_key, reason)
        except Exception as e:
            logger.error("[%s] Failed to write to DLQ '%s': %s", self.role.value, dlq_key, e)

    # ------------------------------------------------------------------ #
    #  Core processing loop                                               #
    # ------------------------------------------------------------------ #
    async def _process_message(self, stream_key: str, msg_id: str, raw_fields: dict) -> None:
        """Decode → process → ack or retry → DLQ."""
        # Decode fields (Redis returns bytes in some drivers)
        fields: Dict[str, Any] = {}
        for k, v in raw_fields.items():
            key = k.decode() if isinstance(k, bytes) else str(k)
            val = v.decode() if isinstance(v, bytes) else v
            if key == "payload_json":
                try:
                    val = json.loads(val)
                except Exception:
                    pass
            fields[key] = val

        # Extract payload
        event_data = fields.get("payload_json", fields)

        retry_count = self._retry_counts.get(msg_id, 0)
        max_retries = self.retry_policy["max_retries"]

        try:
            success = await self.process_event(stream_key, event_data)
            if success:
                if self.redis:
                    await self.redis.xack(stream_key, self.consumer_group, msg_id)
                self._retry_counts.pop(msg_id, None)
            else:
                raise RuntimeError("process_event returned False")
        except Exception as e:
            retry_count += 1
            self._retry_counts[msg_id] = retry_count
            if retry_count >= max_retries:
                logger.error("[%s] Max retries (%d) exhausted for msg %s: %s",
                             self.role.value, max_retries, msg_id, e)
                if self.redis:
                    await self.redis.xack(stream_key, self.consumer_group, msg_id)
                await self._send_to_dlq(stream_key, msg_id, event_data, str(e))
                self._retry_counts.pop(msg_id, None)
            else:
                backoff = self.retry_policy["retry_backoff_s"] * (2 ** (retry_count - 1))
                logger.warning("[%s] Retry %d/%d for msg %s in %ds: %s",
                               self.role.value, retry_count, max_retries, msg_id, backoff, e)
                await asyncio.sleep(min(backoff, 60))

    async def run(self) -> None:
        """Main consumer loop. Call this in an asyncio task."""
        self._running = True
        await self._ensure_consumer_groups()

        claim_interval = 30  # seconds between orphan claim sweeps
        last_claim_ts = time.monotonic()

        while self._running:
            try:
                # Periodic orphan recovery
                now = time.monotonic()
                if now - last_claim_ts > claim_interval:
                    for stream_key in self.streams:
                        if not stream_key.startswith("sentinelai:dl_queue:"):
                            orphans = await self._claim_orphaned_messages(stream_key)
                            for msg_id, raw_fields in (orphans or []):
                                mid = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
                                await self._process_message(stream_key, mid, raw_fields)
                    last_claim_ts = now

                if not self.redis:
                    await asyncio.sleep(2)
                    continue

                # Backpressure check
                bp = False
                for stream_key in self.streams:
                    if not stream_key.startswith("sentinelai:dl_queue:"):
                        if await self._is_backpressured(stream_key):
                            bp = True
                            break
                if bp:
                    await asyncio.sleep(1)
                    continue

                # Read from all assigned streams
                stream_ids = {
                    s: ">" for s in self.streams if not s.startswith("sentinelai:dl_queue:")
                }
                if not stream_ids:
                    await asyncio.sleep(2)
                    continue

                results = await self.redis.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    stream_ids,
                    count=10,
                    block=2000
                )

                if not results:
                    continue

                for stream_key, messages in (results or []):
                    sk = stream_key.decode() if isinstance(stream_key, bytes) else str(stream_key)
                    for msg_id, raw_fields in (messages or []):
                        mid = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
                        await self._process_message(sk, mid, raw_fields)

            except asyncio.CancelledError:
                logger.info("[%s] Consumer loop cancelled", self.role.value)
                break
            except Exception as e:
                logger.exception("[%s] Consumer loop error: %s", self.role.value, e)
                await asyncio.sleep(2)

    def stop(self) -> None:
        """Signals the consumer loop to stop gracefully."""
        self._running = False
