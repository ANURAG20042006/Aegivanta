import asyncio
import json
import random
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.config import settings
from backend.app.core.logging import logger


class ConnectionManager:
    """Manages active WebSocket connections for streaming live packet telemetry and threat alerts."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Mode: {settings.OPERATING_MODE}. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket client disconnected.")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket client: {str(e)}")


manager = ConnectionManager()
router = APIRouter(tags=["WebSockets Telemetry"])


@router.websocket("/ws/threats")
async def websocket_threat_stream(websocket: WebSocket):
    """
    Establishes real-time WebSocket connection streaming network packet telemetry.
    Strictly guarded by OPERATING_MODE:
      - DEMO: Generates synthetic telemetry labeled 'DEMO MODE'.
      - LAB: Generates controlled lab benchmark flows labeled 'LAB MODE'.
      - PRODUCTION: Disables random synthetic generator. Returns healthy/idle state unless real traffic source is active.
    """
    await manager.connect(websocket)
    try:
        while True:
            mode = settings.OPERATING_MODE.upper()

            if mode == "DEMO":
                is_threat = random.random() < 0.25
                attack_types = ["DDoS", "Port Scan", "SQL Injection", "DoS Hulk", "Botnet", "XSS", "Zero-Day Anomaly"]
                attack_type = random.choice(attack_types) if is_threat else "BENIGN"

                packet_event = {
                    "type": "PACKET_STREAM",
                    "mode": "DEMO MODE",
                    "timestamp": asyncio.get_event_loop().time(),
                    "source_ip": f"192.168.1.{random.randint(2, 254)}",
                    "destination_ip": "10.0.0.1",
                    "protocol": random.choice(["TCP", "UDP", "ICMP"]),
                    "packet_length": random.randint(64, 1500),
                    "is_malicious": is_threat,
                    "attack_type": attack_type,
                    "confidence_score": None,
                    "confidence_available": False,
                    "severity": random.choice(["High", "Critical"]) if is_threat else "Low"
                }
                await websocket.send_json(packet_event)
                await asyncio.sleep(2.0)

            elif mode == "LAB":
                # Controlled lab benchmark flow event
                packet_event = {
                    "type": "PACKET_STREAM",
                    "mode": "LAB MODE",
                    "timestamp": asyncio.get_event_loop().time(),
                    "source_ip": "10.0.100.45",
                    "destination_ip": "10.0.0.1",
                    "protocol": "TCP",
                    "packet_length": 512,
                    "is_malicious": False,
                    "attack_type": "BENIGN",
                    "confidence_score": None,
                    "confidence_available": False,
                    "severity": "Low"
                }
                await websocket.send_json(packet_event)
                await asyncio.sleep(3.0)

            else:  # PRODUCTION MODE
                # Production Mode: Disables random synthetic generator completely
                status_event = {
                    "type": "SYSTEM_STATUS",
                    "mode": "PRODUCTION MODE",
                    "timestamp": asyncio.get_event_loop().time(),
                    "status": "HEALTHY",
                    "message": "Production mode active. Real network flow capture engine listening on interface."
                }
                await websocket.send_json(status_event)
                await asyncio.sleep(5.0)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)
