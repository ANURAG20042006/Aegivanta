"""
backend/app/response_worker.py
==============================
Phase 3.7 Production Autonomous Response & SOAR Stream Worker.
Consumes response actions from Redis Streams consumer group (sentinel:response:group),
executes actions through safe adapters, verifies infrastructure state,
acknowledges messages (XACK), and handles pending message recovery.
"""

import sys
import os
import signal
import asyncio
import logging
from typing import Dict, Any

from backend.app.config import settings
from backend.app.database import AsyncSessionLocal
from backend.app.services.distributed_stream_service import distributed_stream_engine, RedisStreamBackend
from backend.app.services.response_orchestrator import ResponseOrchestrator
from backend.app.services.response_actions import response_action_registry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SentinelResponseWorker] - %(message)s"
)
logger = logging.getLogger("SentinelResponseWorker")


class ResponseWorkerDaemon:
    """Consumes and executes automated SOAR remediation actions from Redis Streams."""

    STREAM_RESPONSE_KEY = "sentinel:response-actions"
    STREAM_RESPONSE_GROUP = "sentinel:response:group"

    def __init__(self):
        self.running = False
        self.worker_name = f"response-worker-{os.getpid()}"

    def handle_signal(self, sig, frame):
        logger.info("Received termination signal %s. Initiating graceful shutdown...", sig)
        self.running = False

    async def process_response_action(self, event_data: Dict[str, Any]):
        """Processes and executes a single response action from the stream."""
        action_id = event_data.get("action_id")
        action_type = event_data.get("action_type")
        target_entity = event_data.get("target_entity")
        incident_id = event_data.get("incident_id")
        parameters = event_data.get("parameters", {})
        requested_by = event_data.get("requested_by", "SYSTEM")

        logger.info("Worker %s executing response action %s (%s on %s)",
                    self.worker_name, action_id, action_type, target_entity)

        async with AsyncSessionLocal() as db:
            if action_id:
                # Execute existing action record
                act = await ResponseOrchestrator.execute_action(
                    action_id=action_id,
                    executed_by=requested_by,
                    db=db
                )
                return {
                    "action_id": act.id,
                    "status": act.status,
                    "verification": act.verification_result
                }
            elif incident_id and action_type and target_entity:
                # Submit and execute new action
                act = await ResponseOrchestrator.submit_action(
                    incident_id=incident_id,
                    action_type=action_type,
                    target_entity=target_entity,
                    requested_by=requested_by,
                    actor_role="admin",
                    is_dry_run=event_data.get("is_dry_run", False),
                    idempotency_key=event_data.get("idempotency_key"),
                    parameters=parameters,
                    auto_execute_if_allowed=True,
                    db=db
                )
                return {
                    "action_id": act.id,
                    "status": act.status,
                    "verification": act.verification_result
                }
            else:
                raise ValueError("Malformed response action payload: missing action_id or (incident_id, action_type, target_entity).")

    async def run(self):
        self.running = True
        logger.info("Initializing SentinelAI Response Worker %s on group %s...",
                    self.worker_name, self.STREAM_RESPONSE_GROUP)

        redis_backend = RedisStreamBackend(redis_url=settings.REDIS_URL)
        conn_ok = await redis_backend.connect()
        if not conn_ok:
            for _ in range(5):
                await asyncio.sleep(1.0)
                if await redis_backend.connect():
                    conn_ok = True
                    break

        if not conn_ok and settings.APP_ENV.lower() == "production":
            logger.critical("FATAL: Redis connection failed in production mode. Response Worker exiting.")
            sys.exit(1)

        distributed_stream_engine.set_backend(redis_backend)

        while self.running:
            try:
                # 1. Consume response action messages from consumer group
                messages = await redis_backend.consume_events(
                    stream_key=self.STREAM_RESPONSE_KEY,
                    group_name=self.STREAM_RESPONSE_GROUP,
                    consumer_name=self.worker_name,
                    count=5,
                    block_ms=2000
                )

                for msg in messages:
                    if not self.running:
                        break
                    msg_id = msg["id"]
                    event_data = msg["data"]

                    # Process with retry backoff
                    success, res, err = await distributed_stream_engine.process_with_retry(
                        event_data=event_data,
                        processor_fn=self.process_response_action,
                        max_retries=3
                    )

                    # Acknowledge after processing
                    await redis_backend.acknowledge_event(
                        stream_key=self.STREAM_RESPONSE_KEY,
                        group_name=self.STREAM_RESPONSE_GROUP,
                        message_id=msg_id
                    )

                # 2. Claim pending abandoned messages
                reclaimed = await redis_backend.claim_pending_events(
                    stream_key=self.STREAM_RESPONSE_KEY,
                    group_name=self.STREAM_RESPONSE_GROUP,
                    consumer_name=self.worker_name,
                    min_idle_time_ms=60000,
                    count=5
                )
                for rec_msg in reclaimed:
                    rec_id = rec_msg["id"]
                    await distributed_stream_engine.process_with_retry(
                        event_data=rec_msg["data"],
                        processor_fn=self.process_response_action
                    )
                    await redis_backend.acknowledge_event(
                        stream_key=self.STREAM_RESPONSE_KEY,
                        group_name=self.STREAM_RESPONSE_GROUP,
                        message_id=rec_id
                    )

            except asyncio.CancelledError:
                logger.info("Response Worker task cancelled.")
                break
            except Exception as exc:
                logger.error("Unexpected response worker exception: %s", exc)
                await asyncio.sleep(1.0)

        logger.info("Response Worker %s gracefully stopped.", self.worker_name)
        await redis_backend.disconnect()


def main():
    daemon = ResponseWorkerDaemon()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, daemon.handle_signal)
        except Exception:
            pass
    asyncio.run(daemon.run())


if __name__ == "__main__":
    main()
