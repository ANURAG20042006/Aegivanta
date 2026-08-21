"""
backend/app/models/autonomous_control_plane.py
==============================================
Phase 49 — Autonomous Cyber Defense Control Plane & Decisive War Room.

Models:
- AutonomousDefenseMission : High-level strategic autonomous defense mission directives
- DefenseWarRoomSession     : Live multi-agent war room session with real-time tactical consensus
- WarRoomActionDecision    : Granular tactical actions executed under autonomous consensus
"""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, JSON
)
from backend.app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AutonomousDefenseMission(Base):
    """Strategic autonomous defense mission directive."""
    __tablename__ = "autonomous_defense_missions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")

    mission_name = Column(String(200), nullable=False, default="Operation Sovereign Shield")
    mission_code = Column(String(50), nullable=False, default="MISSION-ALPHA-01")
    objective = Column(Text, nullable=False, default="Autonomous containment and threat neutralization across all production VPCs.")
    threat_tier = Column(String(30), nullable=False, default="CRITICAL")  # LOW, MEDIUM, HIGH, CRITICAL, NATION_STATE
    mission_status = Column(String(30), nullable=False, default="ACTIVE")  # PENDING, ACTIVE, COMPLETED, ABORTED

    # Autonomous authorization & bounds
    autonomy_level = Column(String(30), nullable=False, default="FULL_AUTONOMY")  # SUPERVISED, SEMI_AUTONOMOUS, FULL_AUTONOMY
    blast_radius_limit_usd = Column(Float, nullable=False, default=100000.0)
    enforce_human_veto_window_seconds = Column(Integer, nullable=False, default=30)
    kill_switch_engaged = Column(Boolean, nullable=False, default=False)

    # Mission metrics
    actions_executed_count = Column(Integer, nullable=False, default=42)
    threats_neutralized_count = Column(Integer, nullable=False, default=19)
    success_rate = Column(Float, nullable=False, default=0.985)
    started_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    mission_context_json = Column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<AutonomousDefenseMission {self.mission_code} [{self.mission_status}]>"


class DefenseWarRoomSession(Base):
    """Live multi-agent autonomous defense war room session."""
    __tablename__ = "defense_war_room_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")
    mission_id = Column(String(36), nullable=True, index=True)

    room_name = Column(String(200), nullable=False, default="War Room Zero — Threat Outbreak Alpha")
    session_status = Column(String(30), nullable=False, default="ACTIVE")  # ACTIVE, CONCLUDED, PAUSED
    threat_actor_attributed = Column(String(100), nullable=False, default="APT29 / Midnight Blizzard")
    severity = Column(String(20), nullable=False, default="CRITICAL")

    # Multi-Agent Consensus
    participating_agents_json = Column(JSON, nullable=False, default=list)
    consensus_confidence_score = Column(Float, nullable=False, default=0.978)
    active_tactical_plan = Column(Text, nullable=False, default="Isolate affected Kubernetes pods, revoke compromised IAM tokens, and apply dynamic microsegmentation egress filter.")

    # Kill switch & human oversight
    kill_switch_active = Column(Boolean, nullable=False, default=False)
    human_in_the_loop_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    concluded_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<DefenseWarRoomSession {self.room_name} status={self.session_status}>"


class WarRoomActionDecision(Base):
    """Tactical intervention action decided and executed by autonomous agents."""
    __tablename__ = "war_room_action_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True, default="default-tenant")
    war_room_id = Column(String(36), nullable=False, index=True)

    action_name = Column(String(150), nullable=False, default="Revoke Compromised Service Account IAM Keys")
    action_category = Column(String(80), nullable=False, default="CONTAINMENT")  # CONTAINMENT, ERADICATION, ISOLATION, DECEPTION
    proposing_agent = Column(String(80), nullable=False, default="Agent-IdentitySentinel")
    consensus_vote_ratio = Column(Float, nullable=False, default=1.0)  # 1.0 = 100% agent unanimous consensus
    execution_status = Column(String(30), nullable=False, default="EXECUTED")  # PENDING, EXECUTED, VETOED, FAILED
    execution_latency_ms = Column(Float, nullable=False, default=32.4)
    target_entity = Column(String(200), nullable=False, default="sa-cloud-ingest@aegivanta-prod.iam.gserviceaccount.com")

    action_payload_json = Column(JSON, nullable=False, default=dict)
    executed_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:
        return f"<WarRoomActionDecision {self.action_name} status={self.execution_status}>"
