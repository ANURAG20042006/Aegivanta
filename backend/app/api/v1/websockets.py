import asyncio
import json
import random
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.core.logging import logger


class ConnectionManager:
    """Manages active WebSocket connections for streaming live packet telemetry and threat alerts."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

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
    """Establishes real-time WebSocket connection streaming synthetic network packet telemetry and threat notifications."""
    await manager.connect(websocket)
    try:
        while True:
            # Simulate real-time packet stream telemetry event
            is_threat = random.random() < 0.25  # 25% chance of threat
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
                "confidence_score": round(random.uniform(0.88, 0.99) if is_threat else random.uniform(0.95, 0.99), 4),
                "severity": random.choice(["High", "Critical"]) if is_threat else "Low"
            }

            await websocket.send_text(json.dumps(packet_event))
            await asyncio.sleep(1.5)  # Push telemetry every 1.5 seconds

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket stream error: {str(e)}")
        manager.disconnect(websocket)
