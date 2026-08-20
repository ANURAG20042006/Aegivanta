"""
backend/app/services/distributed_stream_service.py
==================================================
Phase 3.2 Distributed Streaming Infrastructure:
Redis Streams, Consumer Groups, Cross-Worker Atomic Idempotency, Durable DLQ,
and Multi-Instance Redis Pub/Sub WebSocket Backplane.
"""

import os
import json
import time
import uuid
import hashlib
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Callable, Awaitable
from datetime import datetime, timezone

try:
    import redis.asyncio as aioredis
    HAS_AIOREDIS = True
except ImportError:
    HAS_AIOREDIS = False

from backend.app.config import settings

logger = logging.getLogger("SentinelAI")


class EventStreamBackend(ABC):
    """Abstract interface for event streaming, consumer groups, and atomic idempotency."""

    @abstractmethod
    async def connect(self) -> bool:
        """Establishes connection to the streaming backend."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Closes connection to the streaming backend."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Returns True if the backend is actively connected."""
        pass

    @abstractmethod
    async def publish_event(self, stream_key: str, event_data: Dict[str, Any]) -> str:
        """Publishes an event to a durable stream. Returns message ID."""
        pass

    @abstractmethod
    async def consume_events(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        count: int = 10,
        block_ms: int = 2000
    ) -> List[Dict[str, Any]]:
        """Consumes unacknowledged events from a consumer group."""
        pass

    @abstractmethod
    async def acknowledge_event(self, stream_key: str, group_name: str, message_id: str) -> bool:
        """Acknowledges (XACK) processed event."""
        pass

    @abstractmethod
    async def claim_pending_events(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        min_idle_time_ms: int = 60000,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Claims abandoned/stale messages from other crashed consumers."""
        pass

    @abstractmethod
    async def check_and_set_idempotency(self, dedup_key: str, ttl_seconds: int = 86400) -> bool:
        """
        Atomic Check-and-Set (SET NX EX).
        Returns True if key was set (FIRST TIME SEEN - allowed to process).
        Returns False if key already existed (DUPLICATE - reject).
        """
        pass

    @abstractmethod
    async def push_to_dlq(
        self,
        dlq_key: str,
        event_payload: Dict[str, Any],
        reason: str,
        attempts: int,
        source_worker: str
    ) -> str:
        """Persists a failed event into the durable Dead Letter Queue stream."""
        pass

    @abstractmethod
    async def list_dlq(self, dlq_key: str, count: int = 50) -> List[Dict[str, Any]]:
        """Lists entries in the Dead Letter Queue stream."""
        pass

    @abstractmethod
    async def delete_dlq_event(self, dlq_key: str, message_id: str) -> bool:
        """Deletes an acknowledged or remediated event from the DLQ stream."""
        pass

    @abstractmethod
    async def publish_pubsub(self, channel: str, message: Dict[str, Any]) -> int:
        """Publishes a broadcast event to Redis Pub/Sub channel."""
        pass


class InMemoryStreamBackend(EventStreamBackend):
    """
    In-memory streaming backend for testing, local fallback, and zero-dependency environments.
    Implements stream semantics, atomic deduplication, and DLQ.
    """

    def __init__(self):
        self._connected = True
        self._streams: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        self._idempotency_store: Dict[str, float] = {}
        self._dlq: Dict[str, List[Dict[str, Any]]] = {}
        self._pubsub_subscribers: Dict[str, List[Callable]] = {}
        self._pending_acks: Dict[str, Dict[str, Dict[str, Any]]] = {}  # group -> {msg_id: data}

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    async def publish_event(self, stream_key: str, event_data: Dict[str, Any]) -> str:
        msg_id = f"{int(time.time() * 1000)}-{len(self._streams.get(stream_key, []))}"
        if stream_key not in self._streams:
            self._streams[stream_key] = []
        self._streams[stream_key].append((msg_id, dict(event_data)))
        return msg_id

    async def consume_events(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        count: int = 10,
        block_ms: int = 2000
    ) -> List[Dict[str, Any]]:
        if stream_key not in self._streams:
            return []

        group_pending = self._pending_acks.setdefault(group_name, {})
        messages = self._streams[stream_key]

        unclaimed = []
        for msg_id, data in messages:
            if msg_id not in group_pending:
                item = {
                    "id": msg_id,
                    "stream": stream_key,
                    "data": data,
                    "claimed_by": consumer_name,
                    "claimed_at": time.time()
                }
                group_pending[msg_id] = item
                unclaimed.append(item)
                if len(unclaimed) >= count:
                    break
        return unclaimed

    async def acknowledge_event(self, stream_key: str, group_name: str, message_id: str) -> bool:
        group_pending = self._pending_acks.get(group_name, {})
        if message_id in group_pending:
            del group_pending[message_id]
            return True
        return False

    async def claim_pending_events(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        min_idle_time_ms: int = 60000,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        group_pending = self._pending_acks.get(group_name, {})
        now = time.time()
        claimed = []
        for msg_id, item in list(group_pending.items()):
            idle_ms = (now - item.get("claimed_at", now)) * 1000.0
            if idle_ms >= min_idle_time_ms:
                item["claimed_by"] = consumer_name
                item["claimed_at"] = now
                claimed.append(item)
                if len(claimed) >= count:
                    break
        return claimed

    async def check_and_set_idempotency(self, dedup_key: str, ttl_seconds: int = 86400) -> bool:
        now = time.time()
        # Clean expired keys
        expired = [k for k, exp in self._idempotency_store.items() if exp < now]
        for k in expired:
            del self._idempotency_store[k]

        if dedup_key in self._idempotency_store:
            return False  # Already seen (Duplicate)

        self._idempotency_store[dedup_key] = now + ttl_seconds
        return True  # First time seen

    async def push_to_dlq(
        self,
        dlq_key: str,
        event_payload: Dict[str, Any],
        reason: str,
        attempts: int,
        source_worker: str
    ) -> str:
        dlq_id = f"dlq-{uuid.uuid4().hex[:12]}"
        entry = {
            "dlq_id": dlq_id,
            "event_id": event_payload.get("event_id", dlq_id),
            "payload": event_payload,
            "failure_reason": reason,
            "attempts": attempts,
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "source_worker": source_worker
        }
        if dlq_key not in self._dlq:
            self._dlq[dlq_key] = []
        self._dlq[dlq_key].append(entry)
        return dlq_id

    async def list_dlq(self, dlq_key: str, count: int = 50) -> List[Dict[str, Any]]:
        return list(self._dlq.get(dlq_key, []))[-count:]

    async def delete_dlq_event(self, dlq_key: str, message_id: str) -> bool:
        entries = self._dlq.get(dlq_key, [])
        initial_len = len(entries)
        self._dlq[dlq_key] = [e for e in entries if e.get("dlq_id") != message_id and e.get("event_id") != message_id]
        return len(self._dlq[dlq_key]) < initial_len

    async def publish_pubsub(self, channel: str, message: Dict[str, Any]) -> int:
        subs = self._pubsub_subscribers.get(channel, [])
        for sub in subs:
            try:
                if asyncio.iscoroutinefunction(sub):
                    asyncio.create_task(sub(message))
                else:
                    sub(message)
            except Exception as e:
                logger.error("PubSub subscriber error: %s", e)
        return len(subs)


class RedisStreamBackend(EventStreamBackend):
    """
    Production-grade Redis Streams & Consumer Groups backend with persistent DLQ,
    atomic check-and-set idempotency, and Redis Pub/Sub WebSocket backplane.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._client: Optional[Any] = None
        self._connected = False

    async def connect(self) -> bool:
        if not HAS_AIOREDIS:
            logger.warning("redis-py is not installed; falling back to in-memory streaming backend.")
            self._connected = False
            return False

        try:
            self._client = aioredis.from_url(
                self.redis_url,
                decode_responses=True,
                protocol=2,
                socket_timeout=5.0,
                socket_connect_timeout=5.0
            )
            # Health ping
            await self._client.ping()
            self._connected = True
            logger.info("Connected successfully to Redis Stream broker at %s", self.redis_url.split("@")[-1])
            return True
        except Exception as exc:
            self._connected = False
            logger.warning("Redis connection failed (%s); streaming engine operating in resilient fallback mode.", exc)
            return False

    async def disconnect(self) -> None:
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
        self._connected = False

    def is_connected(self) -> bool:
        return bool(self._connected and self._client is not None)

    async def _ensure_consumer_group(self, stream_key: str, group_name: str):
        """Ensures the consumer group exists on the stream."""
        if not self.is_connected():
            return
        try:
            await self._client.xgroup_create(stream_key, group_name, id="0", mkstream=True)
        except Exception as e:
            # BUSYGROUP Consumer Group name already exists
            if "BUSYGROUP" not in str(e):
                logger.debug("xgroup_create notice: %s", e)

    async def publish_event(self, stream_key: str, event_data: Dict[str, Any]) -> str:
        if not self.is_connected():
            raise ConnectionError("Redis is not connected.")

        # Serialize payload dictionary to JSON string in field 'payload'
        payload_json = json.dumps(event_data)
        msg_id = await self._client.xadd(stream_key, {"payload": payload_json})
        return str(msg_id)

    async def consume_events(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        count: int = 10,
        block_ms: int = 2000
    ) -> List[Dict[str, Any]]:
        if not self.is_connected():
            return []

        await self._ensure_consumer_group(stream_key, group_name)

        try:
            # Read new messages for this consumer group (ID '>')
            raw_res = await self._client.xreadgroup(
                groupname=group_name,
                consumername=consumer_name,
                streams={stream_key: ">"},
                count=count,
                block=block_ms
            )
            results = []
            if raw_res:
                for stream, msgs in raw_res:
                    for msg_id, fields in msgs:
                        try:
                            data = json.loads(fields.get("payload", "{}"))
                        except Exception:
                            data = fields
                        results.append({
                            "id": msg_id,
                            "stream": stream,
                            "data": data,
                            "claimed_by": consumer_name
                        })
            return results
        except Exception as exc:
            logger.error("Error reading from Redis Stream %s: %s", stream_key, exc)
            return []

    async def acknowledge_event(self, stream_key: str, group_name: str, message_id: str) -> bool:
        if not self.is_connected():
            return False
        try:
            res = await self._client.xack(stream_key, group_name, message_id)
            return bool(res > 0)
        except Exception as exc:
            logger.error("Error acknowledging Redis message %s: %s", message_id, exc)
            return False

    async def claim_pending_events(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        min_idle_time_ms: int = 60000,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        if not self.is_connected():
            return []
        try:
            # xautoclaim reclaims abandoned messages from dead workers
            claim_res = await self._client.xautoclaim(
                name=stream_key,
                groupname=group_name,
                consumername=consumer_name,
                min_idle_time=min_idle_time_ms,
                start_id="0-0",
                count=count
            )
            claimed = []
            if claim_res and len(claim_res) >= 2:
                msgs = claim_res[1]
                for msg_id, fields in msgs:
                    try:
                        data = json.loads(fields.get("payload", "{}"))
                    except Exception:
                        data = fields
                    claimed.append({
                        "id": msg_id,
                        "stream": stream_key,
                        "data": data,
                        "claimed_by": consumer_name
                    })
            return claimed
        except Exception as exc:
            logger.debug("Pending message claim check: %s", exc)
            return []

    async def check_and_set_idempotency(self, dedup_key: str, ttl_seconds: int = 86400) -> bool:
        if not self.is_connected():
            return True  # Fallback: allow if Redis offline

        redis_key = f"sentinel:idempotency:{dedup_key}"
        try:
            # SET key value NX EX ttl (Atomic Check-and-Set)
            # Returns True if key was set (First time seen), None/False if existed (Duplicate)
            res = await self._client.set(redis_key, "1", ex=ttl_seconds, nx=True)
            return bool(res)
        except Exception as exc:
            logger.error("Redis atomic idempotency check failed: %s", exc)
            return True

    async def push_to_dlq(
        self,
        dlq_key: str,
        event_payload: Dict[str, Any],
        reason: str,
        attempts: int,
        source_worker: str
    ) -> str:
        if not self.is_connected():
            return ""

        entry = {
            "event_id": event_payload.get("event_id", str(uuid.uuid4())),
            "payload": event_payload,
            "failure_reason": reason,
            "attempts": attempts,
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "source_worker": source_worker
        }
        entry_json = json.dumps(entry)
        msg_id = await self._client.xadd(dlq_key, {"payload": entry_json})
        return str(msg_id)

    async def list_dlq(self, dlq_key: str, count: int = 50) -> List[Dict[str, Any]]:
        if not self.is_connected():
            return []
        try:
            raw_res = await self._client.xrevrange(dlq_key, max="+", min="-", count=count)
            entries = []
            for msg_id, fields in raw_res:
                try:
                    data = json.loads(fields.get("payload", "{}"))
                    data["dlq_id"] = msg_id
                    entries.append(data)
                except Exception:
                    entries.append({"dlq_id": msg_id, "raw": fields})
            return entries
        except Exception as exc:
            logger.error("Error listing DLQ entries: %s", exc)
            return []

    async def delete_dlq_event(self, dlq_key: str, message_id: str) -> bool:
        if not self.is_connected():
            return False
        try:
            res = await self._client.xdel(dlq_key, message_id)
            return bool(res > 0)
        except Exception as exc:
            logger.error("Error deleting DLQ event %s: %s", message_id, exc)
            return False

    async def publish_pubsub(self, channel: str, message: Dict[str, Any]) -> int:
        if not self.is_connected():
            return 0
        try:
            msg_str = json.dumps(message)
            receivers = await self._client.publish(channel, msg_str)
            return int(receivers)
        except Exception as exc:
            logger.error("Redis PubSub publish error on %s: %s", channel, exc)
            return 0


class DistributedStreamEngine:
    """
    Master Distributed Streaming & Observability Coordinator for SentinelAI.
    Coordinates publisher, consumer group workers, retry exponential backoff,
    cross-worker idempotency, and persistent DLQ routing.
    """

    def __init__(self, backend: Optional[EventStreamBackend] = None):
        self.backend: EventStreamBackend = backend or InMemoryStreamBackend()
        self.worker_id = f"worker-{os.getpid()}-{uuid.uuid4().hex[:6]}"

        # Prometheus metrics counters
        self.metrics = {
            "published_total": 0,
            "consumed_total": 0,
            "acked_total": 0,
            "failed_total": 0,
            "retried_total": 0,
            "dlq_total": 0,
            "duplicate_total": 0,
            "pubsub_published_total": 0,
            "pubsub_received_total": 0,
            "websocket_broadcast_total": 0
        }

    async def initialize(self):
        """Initializes connection to backend."""
        await self.backend.connect()

    def set_backend(self, backend: EventStreamBackend):
        """Swaps the streaming backend (e.g. for testing with InMemory or FakeRedis)."""
        self.backend = backend

    def compute_event_hash(self, payload: Dict[str, Any]) -> str:
        """Computes deterministic SHA256 idempotency fingerprint from core flow parameters."""
        core_keys = [
            str(payload.get("source_ip", "")),
            str(payload.get("destination_ip", "")),
            str(payload.get("source_port", "")),
            str(payload.get("destination_port", "")),
            str(payload.get("protocol", "")),
            f"{float(payload.get('flow_duration', 0.0)):.2f}",
            f"{float(payload.get('total_fwd_packets', 0.0)):.0f}",
            f"{float(payload.get('packet_length_mean', 0.0)):.2f}"
        ]
        digest_str = "|".join(core_keys)
        return hashlib.sha256(digest_str.encode("utf-8")).hexdigest()

    async def ingest_event(
        self,
        event_payload: Dict[str, Any],
        stream_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Durable Event Ingestion Entrypoint with Cross-Worker Atomic Idempotency.
        """
        stream_name = stream_key or settings.STREAM_TELEMETRY_KEY
        event_id = event_payload.get("event_id") or f"evt-{uuid.uuid4().hex}"
        event_payload["event_id"] = event_id
        event_payload["ingested_at"] = datetime.now(timezone.utc).isoformat()
        event_payload["source_worker"] = self.worker_id

        # 1. Cross-Worker Atomic Idempotency Check
        dedup_hash = self.compute_event_hash(event_payload.get("features", event_payload))
        is_first_seen = await self.backend.check_and_set_idempotency(
            dedup_hash, ttl_seconds=settings.STREAM_IDEMPOTENCY_TTL_SECONDS
        )

        if not is_first_seen:
            self.metrics["duplicate_total"] += 1
            return {
                "status": "DUPLICATE",
                "event_id": event_id,
                "dedup_hash": dedup_hash,
                "message": "Duplicate event fingerprint rejected by distributed atomic gate."
            }

        # 2. Publish to Durable Stream
        try:
            msg_id = await self.backend.publish_event(stream_name, event_payload)
            self.metrics["published_total"] += 1
            return {
                "status": "QUEUED",
                "event_id": event_id,
                "stream_id": msg_id,
                "stream_name": stream_name,
                "dedup_hash": dedup_hash
            }
        except Exception as exc:
            self.metrics["failed_total"] += 1
            logger.error("Failed to publish to stream %s: %s", stream_name, exc)
            # Route to DLQ on publish failure
            dlq_id = await self.backend.push_to_dlq(
                settings.STREAM_DLQ_KEY,
                event_payload,
                reason=f"Publish Failure: {str(exc)}",
                attempts=1,
                source_worker=self.worker_id
            )
            self.metrics["dlq_total"] += 1
            return {
                "status": "ROUTED_TO_DLQ",
                "event_id": event_id,
                "dlq_id": dlq_id,
                "error": str(exc)
            }

    async def process_with_retry(
        self,
        event_data: Dict[str, Any],
        processor_fn: Callable[[Dict[str, Any]], Awaitable[Any]],
        max_retries: Optional[int] = None
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        Executes a processing function with exponential backoff retry.
        If all retries fail, routes the event to the durable Dead Letter Queue.
        """
        limit = max_retries or settings.STREAM_MAX_RETRIES
        attempts = 0
        last_error = None

        while attempts < limit:
            attempts += 1
            try:
                res = await processor_fn(event_data)
                self.metrics["consumed_total"] += 1
                return True, res, None
            except Exception as exc:
                last_error = str(exc)
                self.metrics["retried_total"] += 1
                logger.warning(
                    "Worker %s: Attempt %d/%d failed for event %s: %s",
                    self.worker_id, attempts, limit, event_data.get("event_id"), exc
                )
                if attempts < limit:
                    backoff_delay = (2 ** (attempts - 1)) * 0.05  # 50ms, 100ms, 200ms...
                    await asyncio.sleep(backoff_delay)

        # Retries exhausted -> route to Durable DLQ
        self.metrics["failed_total"] += 1
        dlq_id = await self.backend.push_to_dlq(
            settings.STREAM_DLQ_KEY,
            event_data,
            reason=f"Retries Exhausted ({limit} attempts): {last_error}",
            attempts=attempts,
            source_worker=self.worker_id
        )
        self.metrics["dlq_total"] += 1
        logger.error(
            "Event %s exceeded retry limit. Persisted to DLQ %s as %s",
            event_data.get("event_id"), settings.STREAM_DLQ_KEY, dlq_id
        )
        return False, None, last_error

    async def replay_dlq_event(
        self,
        dlq_message_id: str,
        dlq_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Replays a dead-lettered event back into the active processing stream.
        """
        dlq_name = dlq_key or settings.STREAM_DLQ_KEY
        entries = await self.backend.list_dlq(dlq_name, count=100)
        target_entry = None
        for entry in entries:
            if entry.get("dlq_id") == dlq_message_id or entry.get("event_id") == dlq_message_id:
                target_entry = entry
                break

        if not target_entry:
            return {"status": "NOT_FOUND", "message": f"DLQ entry {dlq_message_id} not found."}

        payload = target_entry.get("payload", target_entry)
        # Republish to telemetry stream
        ingest_res = await self.ingest_event(payload)

        # Remove from DLQ
        await self.backend.delete_dlq_event(dlq_name, target_entry.get("dlq_id", dlq_message_id))
        return {
            "status": "REPLAYED",
            "original_dlq_id": dlq_message_id,
            "reingest_result": ingest_res
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Returns Prometheus-compatible stream telemetry counters."""
        return {
            **self.metrics,
            "is_connected": self.backend.is_connected(),
            "worker_id": self.worker_id
        }


# Global Singleton Engine Instance
distributed_stream_engine = DistributedStreamEngine()
