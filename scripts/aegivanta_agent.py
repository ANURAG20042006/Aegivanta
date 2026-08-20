#!/usr/bin/env python3
"""
scripts/aegivanta_agent.py
==========================
Aegivanta Lightweight Customer Telemetry Sensor Agent.
Zero-heavy external dependencies (pure Python 3 standard library).

Features:
- Periodic heartbeat monitoring
- Local in-memory offline buffering
- Gzip-compressed batch telemetry delivery
- Multi-event ingestion (Network flows, Auth events, DNS, HTTP, System)
"""

import sys
import os
import time
import json
import gzip
import urllib.request
import urllib.error
import argparse
import socket
import platform
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] AegivantaAgent: %(message)s"
)
logger = logging.getLogger("AegivantaAgent")


class AegivantaSensorAgent:
    def __init__(self, sensor_id: str, token: str, api_url: str, batch_size: int = 50, heartbeat_interval: int = 30):
        self.sensor_id = sensor_id
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.batch_size = batch_size
        self.heartbeat_interval = heartbeat_interval
        self.buffer = []
        self.seq_id = 1
        self.is_running = True
        self.last_heartbeat_time = 0

    def collect_sample_telemetry(self):
        """Generates realistic local system and network connection telemetry."""
        hostname = socket.gethostname()
        
        # 1. Network Flow Sample
        self.buffer.append({
            "seq_id": self.seq_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": "NETWORK_FLOW",
            "data": {
                "src_ip": "10.0.0.15",
                "dst_ip": "1.1.1.1",
                "src_port": 54321,
                "dst_port": 443,
                "protocol": "TCP",
                "bytes": 1024,
                "packets": 8
            }
        })
        self.seq_id += 1

        # 2. System / Auth Event Sample
        self.buffer.append({
            "seq_id": self.seq_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": "AUTH_EVENT",
            "data": {
                "user": "sec_analyst",
                "src_ip": "10.0.0.15",
                "success": True,
                "privilege_level": "standard"
            }
        })
        self.seq_id += 1

    def send_heartbeat(self):
        """Sends periodic heartbeat with queue statistics."""
        url = f"{self.api_url}/api/v1/sensors/{self.sensor_id}/heartbeat"
        payload = {
            "token": self.token,
            "stats": {
                "queued_events": len(self.buffer),
                "hostname": socket.gethostname(),
                "os": platform.system()
            }
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    logger.debug("Heartbeat acknowledged.")
                    self.last_heartbeat_time = time.time()
        except Exception as e:
            logger.warning("Heartbeat failed: %s", str(e))

    def flush_buffer(self):
        """Compresses and sends batched telemetry to the ingestion gateway."""
        if not self.buffer:
            return

        batch_to_send = self.buffer[:self.batch_size]
        payload = {
            "schema_version": "v1",
            "events": batch_to_send,
            "buffer_stats": {"queued_events": len(self.buffer)}
        }

        json_bytes = json.dumps(payload).encode("utf-8")
        compressed_bytes = gzip.compress(json_bytes)

        url = f"{self.api_url}/api/v1/sensors/ingest"
        req = urllib.request.Request(
            url,
            data=compressed_bytes,
            headers={
                "Content-Type": "application/json",
                "Content-Encoding": "gzip",
                "X-Sensor-ID": self.sensor_id,
                "X-Sensor-Token": self.token
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    # Successfully sent, remove from buffer
                    self.buffer = self.buffer[len(batch_to_send):]
                    logger.info("Flushed %d telemetry events to Aegivanta core.", len(batch_to_send))
        except urllib.error.HTTPError as e:
            logger.error("Ingestion server returned HTTP %d: %s", e.code, e.reason)
        except Exception as e:
            logger.warning("Network offline or connection failed. Retaining %d events in local buffer: %s", len(self.buffer), str(e))

    def run(self):
        """Main agent collection and dispatch loop."""
        logger.info("Aegivanta Sensor Agent started for Sensor ID '%s'", self.sensor_id)
        while self.is_running:
            try:
                # 1. Collect Telemetry
                self.collect_sample_telemetry()

                # 2. Check Heartbeat
                if time.time() - self.last_heartbeat_time >= self.heartbeat_interval:
                    self.send_heartbeat()

                # 3. Flush if buffer reaches batch threshold
                if len(self.buffer) >= self.batch_size:
                    self.flush_buffer()

                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Stopping agent...")
                self.is_running = False
                break
            except Exception as e:
                logger.error("Unexpected agent error: %s", str(e))
                time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aegivanta Lightweight Sensor Agent")
    parser.add_argument("--sensor-id", required=True, help="Enrolled Sensor ID")
    parser.add_argument("--token", required=True, help="Enrollment Secret Token")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Aegivanta API Base URL")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch flush size")
    args = parser.parse_args()

    agent = AegivantaSensorAgent(
        sensor_id=args.sensor_id,
        token=args.token,
        api_url=args.api_url,
        batch_size=args.batch_size
    )
    agent.run()
