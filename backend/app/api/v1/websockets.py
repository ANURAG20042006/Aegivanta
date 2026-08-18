"""
backend/app/api/v1/websockets.py
================================
Real-Time WebSocket Telemetry Stream with JWT Authentication,
Role-Based Authorization, Heartbeat/Ping-Pong, and Connection Limits.
"""

import asyncio
import json
import random
from typing import List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from jose import JWTError

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.security import decode_access_token
from backend.app.core.dependencies import normalize_role

# ── Connection limits ────────────────────────────────────────────────────────
MAX_CONNECTIONS: int = 50

# Roles permitted to open a live telemetry stream
ALLOWED_WS_ROLES = {"admin", "analyst", "viewer"}

# Heartbeat: server sends ping every PING_INTERVAL seconds.
# If the client misses PING_MISS_LIMIT consecutive pongs the connection is closed.
PING_INTERVAL: int = 30  # seconds
PING_MISS_LIMIT: int = 2


class ConnectionManager:
    """Manages authenticated WebSocket connections for live SOC telemetry."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"WebSocket client authenticated and connected. "
            f"Mode: {settings.OPERATING_MODE}. "
            f"Total connections: {self.connection_count}"
        )

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket client disconnected. "
                f"Remaining connections: {self.connection_count}"
            )

    async def broadcast(self, message: str) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket client: {e}")
                self.disconnect(connection)

    async def broadcast_event(self, event_type: str, data: dict) -> None:
        """Broadcast a structured JSON event to all connected SOC clients."""
        payload = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast(payload)


manager = ConnectionManager()
router = APIRouter(tags=["WebSockets Telemetry"])


async def _authenticate_websocket(
    websocket: WebSocket,
    token: Optional[str]
) -> Optional[dict]:
    """
    Validates the JWT token supplied as a query parameter.
    Returns the decoded payload on success, or closes the socket and returns
    None on any authentication/authorization failure.

    Close codes used:
        1008 Policy Violation — unauthenticated / unauthorized
        1013 Try Again Later  — server at connection capacity
    """
    # ── Connection cap ───────────────────────────────────────────────────────
    if manager.connection_count >= MAX_CONNECTIONS:
        await websocket.close(
            code=1013,
            reason="Server at maximum WebSocket connection capacity. Try again later."
        )
        logger.warning(
            f"WebSocket connection rejected: capacity limit "
            f"({MAX_CONNECTIONS}) reached."
        )
        return None

    # ── Token presence check ─────────────────────────────────────────────────
    if not token:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication required: supply ?token=<JWT> query parameter."
        )
        logger.warning("WebSocket rejected: missing token.")
        return None

    # ── JWT validation ───────────────────────────────────────────────────────
    try:
        payload = decode_access_token(token)
    except Exception as exc:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Authentication failed: {exc}"
        )
        logger.warning(f"WebSocket rejected: invalid/expired JWT — {exc}")
        return None

    # ── Role-based authorization ─────────────────────────────────────────────
    raw_role: str = payload.get("role", "")
    canonical_role = normalize_role(raw_role)
    if canonical_role not in ALLOWED_WS_ROLES:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Authorization denied: role '{raw_role}' is not permitted."
        )
        logger.warning(
            f"WebSocket rejected: role '{raw_role}' → '{canonical_role}' not in {ALLOWED_WS_ROLES}."
        )
        return None

    return payload


async def _heartbeat(websocket: WebSocket) -> None:
    """
    Sends WebSocket ping frames every PING_INTERVAL seconds.
    Closes the connection if PING_MISS_LIMIT consecutive pongs are missed.
    The FastAPI/Starlette WebSocket implementation raises WebSocketDisconnect
    when the client is gone, which is caught in the parent handler.
    """
    missed = 0
    while True:
        await asyncio.sleep(PING_INTERVAL)
        try:
            await websocket.send_json({"type": "PING"})
            missed = 0
        except Exception:
            missed += 1
            logger.warning(
                f"WebSocket heartbeat: missed pong #{missed} "
                f"(limit={PING_MISS_LIMIT})."
            )
            if missed >= PING_MISS_LIMIT:
                logger.warning("WebSocket heartbeat: closing unresponsive connection.")
                await websocket.close(code=1001, reason="Heartbeat timeout.")
                return


@router.websocket("/ws/threats")
async def websocket_threat_stream(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None, description="JWT bearer token for authentication")
):
    """
    Authenticated real-time WebSocket stream of network packet telemetry and
    threat alerts.

    Authentication:
        Pass the JWT access token as the `token` query parameter:
        ws://host/ws/threats?token=<access_token>

    Authorization:
        Allowed roles: admin, analyst, viewer.
        Disabled or deleted users are rejected.

    Modes (controlled by OPERATING_MODE):
        DEMO       — Synthetic threat telemetry labeled 'DEMO MODE'.
        LAB        — Controlled benchmark flows labeled 'LAB MODE'.
        PRODUCTION — Status heartbeat only; real capture engine required.
    """
    # Authenticate before accept()
    payload = await _authenticate_websocket(websocket, token)
    if payload is None:
        return  # socket already closed inside _authenticate_websocket

    await manager.connect(websocket)

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(_heartbeat(websocket))

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
                status_event = {
                    "type": "SYSTEM_STATUS",
                    "mode": "PRODUCTION MODE",
                    "timestamp": asyncio.get_event_loop().time(),
                    "status": "HEALTHY",
                    "message": (
                        "Production mode active. "
                        "Connect a real network flow capture engine to begin streaming."
                    )
                }
                await websocket.send_json(status_event)
                await asyncio.sleep(5.0)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally.")
    except Exception as e:
        logger.error(f"WebSocket stream error: {e}")
    finally:
        heartbeat_task.cancel()
        manager.disconnect(websocket)
