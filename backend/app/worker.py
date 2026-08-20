"""
backend/app/worker.py
=====================
Phase 3.3 Production Distributed Telemetry Streaming Worker.
Consumes telemetry events from Redis Streams consumer group (sentinel:telemetry:group),
executes ML inference and incident correlation, acknowledges messages (XACK),
and handles graceful shutdown on SIGTERM/SIGINT.
"""

import sys
import os
import signal
import asyncio
import logging
from typing import Dict, Any

from backend.app.config import settings
from backend.app.services.distributed_stream_service import distributed_stream_engine, RedisStreamBackend
from backend.app.services.predict_service import predict_service
from backend.app.schemas.predict import PacketFeatureVector
from backend.app.services.threat_intel_service import ThreatIntelService
from backend.app.services.detection_correlation_service import correlation_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SentinelWorker] - %(message)s"
)
logger = logging.getLogger("SentinelWorker")


class StreamWorkerDaemon:
    def __init__(self):
        self.running = False
        self.worker_name = f"worker-{os.getpid()}"

    def handle_signal(self, sig, frame):
        logger.info("Received termination signal %s. Initiating graceful shutdown...", sig)
        self.running = False

    async def process_telemetry_event(self, event_data: Dict[str, Any]):
        """Processes a single telemetry event through ML inference, TI enrichment, and detection correlation."""
        features = event_data.get("features", event_data)
        try:
            vector = PacketFeatureVector(**features)
            # 1. Run real ML model prediction
            att_type, conf, is_mal, sev, probs, shap = predict_service.infer_packet_threat(
                vector=vector,
                model_name=settings.DEFAULT_MODEL_NAME
            )

            # 2. Fast in-memory Threat Intelligence enrichment (< 0.01ms)
            ioc_matches = ThreatIntelService.cache.fast_check(
                source_ip=getattr(vector, "source_ip", None),
                destination_ip=getattr(vector, "destination_ip", None),
                domain=None
            )
            has_ioc_match = len(ioc_matches) > 0
            if has_ioc_match:
                ioc_sev = ioc_matches[0].get("severity", "HIGH")
                if sev in ["LOW", "MEDIUM", "INFORMATIONAL"] and ioc_sev in ["HIGH", "CRITICAL"]:
                    sev = ioc_sev

            # 3. Detection Correlation & Rule Evaluation (Phase 3.6)
            corr_payload = dict(event_data)
            corr_payload.update({
                "id": event_data.get("event_id") or event_data.get("id"),
                "source_ip": event_data.get("source_ip") or getattr(vector, "source_ip", None),
                "destination_ip": event_data.get("destination_ip") or getattr(vector, "destination_ip", None),
                "destination_port": event_data.get("destination_port") or getattr(vector, "destination_port", None),
                "protocol": event_data.get("protocol") or getattr(vector, "protocol", "TCP"),
                "is_malicious": is_mal or has_ioc_match or bool(event_data.get("is_malicious", False)),
                "attack_type": att_type if (is_mal and att_type != "BENIGN") else event_data.get("attack_type", att_type),
                "confidence": conf if conf > 0.5 else float(event_data.get("confidence", conf)),
                "severity": sev,
                "threat_intel_match": has_ioc_match,
                "matched_iocs": ioc_matches,
                "flow_duration": getattr(vector, "flow_duration", 0.0),
                "timestamp": event_data.get("timestamp")
            })
            corr_bundle = correlation_engine.correlate_event(corr_payload)

            final_malicious = is_mal or has_ioc_match or (corr_bundle is not None) or bool(event_data.get("is_malicious", False))
            final_attack_type = (corr_bundle.get("attack_type") if corr_bundle else None) or (att_type if is_mal else event_data.get("attack_type", att_type))

            logger.debug("Inference complete for event %s: %s (malicious=%s, ti_match=%s, corr=%s)",
                         event_data.get("event_id"), final_attack_type, final_malicious, has_ioc_match, bool(corr_bundle))
            return {
                "attack_type": final_attack_type,
                "confidence": conf,
                "is_malicious": final_malicious,
                "severity": (corr_bundle.get("severity") if corr_bundle else sev),
                "threat_intel_match": has_ioc_match,
                "matched_iocs": ioc_matches,
                "correlation_bundle": corr_bundle
            }
        except Exception as exc:
            logger.error("Error processing telemetry event %s: %s", event_data.get("event_id"), exc)
            raise

    async def run(self):
        self.running = True
        logger.info("Initializing SentinelAI Stream Worker %s on group %s...",
                    self.worker_name, settings.STREAM_CONSUMER_GROUP)

        # Connect to Redis with retry loop
        redis_backend = RedisStreamBackend(redis_url=settings.REDIS_URL)
        conn_ok = await redis_backend.connect()
        if not conn_ok:
            for _ in range(5):
                await asyncio.sleep(1.0)
                if await redis_backend.connect():
                    conn_ok = True
                    break

        if not conn_ok and settings.APP_ENV.lower() == "production":
            logger.critical("FATAL: Redis connection failed in production mode. Worker exiting.")
            sys.exit(1)

        distributed_stream_engine.set_backend(redis_backend)

        # Main Worker Loop
        while self.running:
            try:
                # 1. Consume unacknowledged events from consumer group
                messages = await redis_backend.consume_events(
                    stream_key=settings.STREAM_TELEMETRY_KEY,
                    group_name=settings.STREAM_CONSUMER_GROUP,
                    consumer_name=self.worker_name,
                    count=10,
                    block_ms=2000
                )

                for msg in messages:
                    if not self.running:
                        break
                    msg_id = msg["id"]
                    event_data = msg["data"]

                    # Process with retry exponential backoff
                    success, res, err = await distributed_stream_engine.process_with_retry(
                        event_data=event_data,
                        processor_fn=self.process_telemetry_event,
                        max_retries=settings.STREAM_MAX_RETRIES
                    )

                    # If correlation bundle was created, publish to sentinel:incidents
                    if success and res and res.get("correlation_bundle"):
                        try:
                            await redis_backend.publish_event(
                                stream_key="sentinel:incidents",
                                event_data=res["correlation_bundle"]
                            )
                        except Exception as p_err:
                            logger.debug("Failed to publish incident to Redis stream: %s", p_err)

                    # Acknowledge on success or routing to DLQ
                    await redis_backend.acknowledge_event(
                        stream_key=settings.STREAM_TELEMETRY_KEY,
                        group_name=settings.STREAM_CONSUMER_GROUP,
                        message_id=msg_id
                    )

                # 2. Periodically claim abandoned messages from crashed workers
                reclaimed = await redis_backend.claim_pending_events(
                    stream_key=settings.STREAM_TELEMETRY_KEY,
                    group_name=settings.STREAM_CONSUMER_GROUP,
                    consumer_name=self.worker_name,
                    min_idle_time_ms=60000,
                    count=5
                )
                for rec_msg in reclaimed:
                    rec_id = rec_msg["id"]
                    await distributed_stream_engine.process_with_retry(
                        event_data=rec_msg["data"],
                        processor_fn=self.process_telemetry_event
                    )
                    await redis_backend.acknowledge_event(
                        stream_key=settings.STREAM_TELEMETRY_KEY,
                        group_name=settings.STREAM_CONSUMER_GROUP,
                        message_id=rec_id
                    )

            except asyncio.CancelledError:
                logger.info("Worker task cancelled.")
                break
            except Exception as exc:
                logger.error("Unexpected worker exception: %s", exc)
                await asyncio.sleep(1.0)

        logger.info("Worker %s gracefully stopped.", self.worker_name)
        await redis_backend.disconnect()


def main():
    daemon = StreamWorkerDaemon()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, daemon.handle_signal)
        except Exception:
            pass
    asyncio.run(daemon.run())


if __name__ == "__main__":
    main()
