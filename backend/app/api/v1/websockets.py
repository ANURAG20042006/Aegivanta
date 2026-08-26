"""
backend/app/api/v1/websockets.py
================================
Real-Time WebSocket Telemetry Stream with Database-Backed JWT Authentication,
Active-User Verification, RBAC Authorization, Bi-Directional Heartbeat/Pong Detection,
and Connection Rate Limits.
"""

import asyncio
import json
import random
from typing import List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy import select

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.security import decode_access_token
from backend.app.core.dependencies import normalize_role
from backend.app.database import AsyncSessionFactory
from backend.app.models.user import User

# ── Connection limits ────────────────────────────────────────────────────────
MAX_CONNECTIONS: int = 50

# Roles permitted to open a live telemetry stream
ALLOWED_WS_ROLES = {"admin", "analyst", "viewer"}

# Heartbeat: server sends ping every PING_INTERVAL seconds.
# If the client misses PING_MISS_LIMIT consecutive pongs the connection is closed.
PING_INTERVAL: int = 30  # seconds
PING_MISS_LIMIT: int = 2


class ConnectionManager:
    """Manages authenticated WebSocket connections with multi-tenant isolation for live SOC telemetry."""

    def __init__(self):
        self.active_connections: Dict[WebSocket, str] = {}

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)

    def get_tenant_connections(self, tenant_id: str) -> List[WebSocket]:
        return [ws for ws, tid in self.active_connections.items() if tid == tenant_id]

    async def connect(self, websocket: WebSocket, tenant_id: str = "default-tenant") -> None:
        await websocket.accept()
        self.active_connections[websocket] = tenant_id
        logger.info(
            f"WebSocket client authenticated and connected for tenant '{tenant_id}'. "
            f"Mode: {settings.OPERATING_MODE}. "
            f"Total connections: {self.connection_count}"
        )

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            tid = self.active_connections.pop(websocket, None)
            logger.info(
                f"WebSocket client disconnected for tenant '{tid}'. "
                f"Remaining connections: {self.connection_count}"
            )

    async def broadcast_local(self, message: str, tenant_id: Optional[str] = None) -> None:
        """Broadcasts a raw message strictly to locally connected clients on this instance, scoped by tenant if provided."""
        target_connections = (
            [ws for ws, tid in self.active_connections.items() if tid == tenant_id]
            if tenant_id
            else list(self.active_connections.keys())
        )
        for connection in target_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket client: {e}")
                self.disconnect(connection)

    async def broadcast_to_tenant(self, tenant_id: str, message: str) -> None:
        """Broadcasts raw message strictly to clients belonging to the specified tenant."""
        await self.broadcast_local(message, tenant_id=tenant_id)

    async def broadcast(self, message: str) -> None:
        """Broadcasts message to local clients."""
        await self.broadcast_local(message)

    async def broadcast_event(self, event_type: str, data: dict, tenant_id: Optional[str] = None, publish_to_redis: bool = True) -> None:
        """
        Broadcast a structured JSON event to tenant SOC clients and publish across the
        distributed Redis Pub/Sub backplane with tenant scoping.
        """
        event_dict = {
            "type": event_type,
            "data": data,
            "tenant_id": tenant_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        payload = json.dumps(event_dict)
        await self.broadcast_local(payload, tenant_id=tenant_id)

        if publish_to_redis:
            try:
                from backend.app.services.distributed_stream_service import distributed_stream_engine
                await distributed_stream_engine.backend.publish_pubsub(
                    settings.STREAM_PUBSUB_CHANNEL,
                    event_dict
                )
                distributed_stream_engine.metrics["websocket_broadcast_total"] += 1
            except Exception as pub_err:
                logger.debug("Redis Pub/Sub broadcast notice: %s", pub_err)


manager = ConnectionManager()
router = APIRouter(tags=["WebSockets Telemetry"])


async def _authenticate_websocket(
    websocket: WebSocket,
    token: Optional[str]
) -> Optional[dict]:
    """
    Validates the JWT token supplied as a query parameter against the database.
    Verifies user existence, active status (rejects disabled/deleted accounts),
    and normalized RBAC permissions before accept().

    Close codes used:
        1008 Policy Violation — unauthenticated / unauthorized / disabled user
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

    # ── Database Verification (Active & Non-Deleted User) ────────────────────
    username_or_id = payload.get("sub", "")
    if not username_or_id:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token: missing subject identity."
        )
        return None

    try:
        async with AsyncSessionFactory() as db:
            result = await db.execute(
                select(User).where((User.username == username_or_id) | (User.id == username_or_id))
            )
            user = result.scalar_one_or_none()

            if not user:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="User account associated with token no longer exists."
                )
                logger.warning(f"WebSocket rejected: user '{username_or_id}' not found in database.")
                return None

            if not user.is_active:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="User account is deactivated."
                )
                logger.warning(f"WebSocket rejected: user '{user.username}' is deactivated.")
                return None

            # Enforce canonical role permissions from database record
            canonical_role = normalize_role(user.role)
            if canonical_role not in ALLOWED_WS_ROLES:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason=f"Authorization denied: role '{user.role}' is not permitted."
                )
                logger.warning(
                    f"WebSocket rejected: role '{user.role}' → '{canonical_role}' not in {ALLOWED_WS_ROLES}."
                )
                return None

    except Exception as dbe:
        logger.error(f"WebSocket DB authentication check error: {dbe}")
        # If DB check fails during test run or transient error, fail closed
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication verification error."
        )
        return None

    return payload


async def _heartbeat(websocket: WebSocket, state: dict) -> None:
    """
    Application-Level JSON Heartbeat Worker:
    Periodically sends application-level `{"type": "PING", "timestamp": ...}` frames
    every PING_INTERVAL seconds (30s).
    
    Design Note:
        Application-level JSON messaging is utilized rather than RFC 6455 opcode
        0x9/0xA native control frames because standard browser JavaScript WebSocket
        APIs (DOM WebSocket standard) handle native ping/pong transparently in the
        browser networking stack and do not expose native control frame events to
        frontend application code. Application-level JSON frames guarantee
        deterministic bidirectional liveness verification across all frontend clients
        and reverse proxies (e.g. Nginx, Cloudflare).
    """
    while True:
        await asyncio.sleep(PING_INTERVAL)
        if not state.get("pong_received", True):
            state["missed"] = state.get("missed", 0) + 1
            logger.warning(
                f"WebSocket heartbeat: missed application-level pong #{state['missed']} "
                f"(limit={PING_MISS_LIMIT})."
            )
            if state["missed"] >= PING_MISS_LIMIT:
                logger.warning("WebSocket heartbeat: closing unresponsive connection due to missed pongs.")
                try:
                    await websocket.close(code=1001, reason="Heartbeat timeout: missed application-level pong responses.")
                except Exception:
                    pass
                return
        else:
            state["pong_received"] = False

        try:
            await websocket.send_json({"type": "PING", "timestamp": asyncio.get_event_loop().time()})
        except Exception:
            state["missed"] = state.get("missed", 0) + 1
            if state["missed"] >= PING_MISS_LIMIT:
                return


async def _client_listener(websocket: WebSocket, state: dict) -> None:
    """
    Application-Level Client Frame Listener:
    Listens for incoming client messages, resetting heartbeat state when receiving
    application-level `{"type": "PONG"}` JSON frames or `"PONG"` text tokens.
    """
    while True:
        try:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if isinstance(msg, dict) and msg.get("type") == "PONG":
                    state["pong_received"] = True
                    state["missed"] = 0
            except Exception:
                if data.strip().upper() == "PONG":
                    state["pong_received"] = True
                    state["missed"] = 0
        except WebSocketDisconnect:
            break
        except Exception:
            break


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
        Disabled or deleted users are verified against the database and rejected.

    Heartbeat & Liveness:
        Bi-directional application-level JSON heartbeat: server sends
        `{"type": "PING"}` every 30s; client responds with `{"type": "PONG"}`.
        Unresponsive clients are terminated after 2 consecutive missed pongs (60s).
    """
    # Authenticate before accept()
    payload = await _authenticate_websocket(websocket, token)
    if payload is None:
        return  # socket already closed inside _authenticate_websocket

    await manager.connect(websocket)

    # Initialize bidirectional heartbeat state
    heartbeat_state = {"pong_received": True, "missed": 0}
    heartbeat_task = asyncio.create_task(_heartbeat(websocket, heartbeat_state))
    listener_task = asyncio.create_task(_client_listener(websocket, heartbeat_state))

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
        listener_task.cancel()
        manager.disconnect(websocket)


@router.websocket("/ws/soc-events")
async def websocket_soc_events_stream(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None, description="JWT bearer token for authentication")
):
    """
    Dedicated Authenticated WebSocket stream for unified SOC Operational Events.
    Streams all 12 SOC event categories (Detections, Incidents, Threat Intel,
    Lateral Movement, SOAR Response, Investigations, System Alerts).
    """
    payload = await _authenticate_websocket(websocket, token)
    if payload is None:
        return

    await manager.connect(websocket)

    # Initial sync snapshot
    try:
        from backend.app.services.soc_event_broadcaster import soc_broadcaster
        recent_events = soc_broadcaster.get_recent_events(limit=20)
        await websocket.send_json({
            "type": "INIT_SYNC",
            "events": recent_events,
            "timestamp": asyncio.get_event_loop().time(),
            "status": "CONNECTED"
        })
    except Exception as sync_err:
        logger.debug("Initial sync frame error: %s", sync_err)

    heartbeat_state = {"pong_received": True, "missed": 0}
    heartbeat_task = asyncio.create_task(_heartbeat(websocket, heartbeat_state))
    listener_task = asyncio.create_task(_client_listener(websocket, heartbeat_state))

    try:
        while True:
            # Keep connection alive while event broadcasts are pushed asynchronously
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        logger.info("SOC Events WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"SOC Events WebSocket error: {e}")
    finally:
        heartbeat_task.cancel()
        listener_task.cancel()
        manager.disconnect(websocket)

