"""
backend/app/services/incident_service.py
========================================
Phase 3.6 Incident Aggregation, Deduplication, Lifecycle Management, and Statistics Service.
"""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident, is_valid_state_transition, VALID_INCIDENT_STATUSES
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.models.alert import Alert
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.services.risk_scoring_service import RiskScoringService

logger = logging.getLogger("SentinelAI")


class IncidentService:
    """
    Manages end-to-end incident formation, automated deduplication,
    status transitions, analyst assignments, and operational statistics.
    """

    @staticmethod
    async def create_or_update_from_correlation(
        bundle: Dict[str, Any],
        db: AsyncSession
    ) -> Tuple[Incident, bool]:
        """
        Aggregates a correlation bundle into the incident store.
        Deduplicates against active (OPEN/DETECTED/INVESTIGATING/TRIAGED) incidents matching the same source/dest flow or asset.
        Returns: (incident, is_newly_created)
        """
        src = bundle.get("source_ip", "0.0.0.0")
        dst = bundle.get("destination_ip", "0.0.0.0")
        asset_id = bundle.get("asset_id")

        # 1. Search for existing active incident to aggregate
        active_statuses = ["OPEN", "DETECTED", "TRIAGED", "INVESTIGATING"]
        query = select(Incident).where(
            Incident.status.in_(active_statuses),
            (
                ((Incident.source_ip == src) & (Incident.destination_ip == dst)) |
                (Incident.asset_id == asset_id if asset_id else False)
            )
        ).order_by(desc(Incident.last_seen)).limit(1)

        res = await db.execute(query)
        existing = res.scalar_one_or_none()

        sev_order = {"INFORMATIONAL": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4, "CRITICAL": 5}
        new_sev = bundle.get("severity", "MEDIUM").capitalize()

        if existing:
            # Aggregate into existing incident
            existing.alert_count += bundle.get("event_count", 1)
            existing.last_seen = datetime.now(timezone.utc)

            # Elevate severity if higher
            curr_rank = sev_order.get(existing.severity.upper(), 3)
            new_rank = sev_order.get(new_sev.upper(), 3)
            if new_rank > curr_rank:
                existing.severity = new_sev

            # Update risk score to maximum
            if bundle.get("risk_score", 0.0) > existing.risk_score:
                existing.risk_score = bundle["risk_score"]

            if bundle.get("attack_type"):
                existing.attack_type = bundle["attack_type"]

            # Add timeline event
            timeline_ev = IncidentTimelineEvent(
                incident_id=existing.id,
                event_type="ALERT_CORRELATED",
                title=f"Aggregated {bundle.get('event_count', 1)} Correlated Events",
                description=bundle.get("detection_reason", "Correlated security activity in active window."),
                actor="CORRELATION_ENGINE",
                metadata_payload={
                    "correlation_id": bundle.get("correlation_id"),
                    "matched_rules": bundle.get("matched_rules"),
                    "risk_score": existing.risk_score
                }
            )
            db.add(timeline_ev)
            await db.commit()
            await db.refresh(existing)
            logger.info("Aggregated correlation bundle into existing incident %s (total alerts: %d)",
                        existing.incident_code, existing.alert_count)
            return existing, False

        # 2. Form new Incident
        inc_id = str(uuid.uuid4())
        inc_code = f"INC-{uuid.uuid4().hex[:8].upper()}"
        alt_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"

        new_inc = Incident(
            id=inc_id,
            incident_code=inc_code,
            alert_id=alt_id,
            asset_id=asset_id,
            title=f"Incident: {bundle.get('attack_type', 'Suspicious Activity')}",
            description=bundle.get("detection_reason"),
            status="OPEN",
            risk_score=bundle.get("risk_score", 50.0),
            alert_count=bundle.get("event_count", 1),
            source_ip=src,
            destination_ip=dst,
            source_port=int(bundle.get("source_port", 0) or 0),
            destination_port=int(bundle.get("destination_port", 0) or 0),
            protocol=str(bundle.get("protocol", "TCP")),
            packet_length=int(bundle.get("packet_length", 0) or 0),
            flow_duration=float(bundle.get("flow_duration", 0.0) or 0.0),
            attack_type=str(bundle.get("attack_type", "Threat Activity")),
            confidence_score=float(bundle.get("confidence", 0.85)),
            is_malicious=True,
            severity=new_sev,
            model_name="SentinelAI-Correlator",
            model_version="correlation-v1.0",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
            feature_payload={
                "correlation_id": bundle.get("correlation_id"),
                "matched_rules": bundle.get("matched_rules"),
                "mitre_techniques": bundle.get("mitre_techniques"),
                "risk_components": bundle.get("risk_components")
            }
        )
        db.add(new_inc)

        # Add initial timeline detection
        initial_timeline = IncidentTimelineEvent(
            incident_id=inc_id,
            event_type="DETECTION",
            title="Incident Triggered & Formed",
            description=f"Formed incident from detection correlation: {bundle.get('detection_reason')}",
            actor="CORRELATION_ENGINE",
            metadata_payload={
                "matched_rules": bundle.get("matched_rules"),
                "mitre_techniques": bundle.get("mitre_techniques"),
                "risk_score": new_inc.risk_score
            }
        )
        db.add(initial_timeline)
        await db.commit()
        await db.refresh(new_inc)
        logger.info("Formed new incident %s (%s, Risk: %.1f)", new_inc.incident_code, new_inc.severity, new_inc.risk_score)
        return new_inc, True

    @staticmethod
    async def update_status(
        incident_id: str,
        new_status: str,
        notes: Optional[str],
        analyst: Optional[str],
        db: AsyncSession
    ) -> Incident:
        """Transitions incident status with strict state machine validation and timeline recording."""
        target_status = new_status.upper()
        if target_status not in VALID_INCIDENT_STATUSES:
            raise ValueError(f"Invalid incident status '{new_status}'. Allowed: {VALID_INCIDENT_STATUSES}")

        query = select(Incident).where(
            (Incident.id == incident_id) | (Incident.incident_code == incident_id)
        )
        res = await db.execute(query)
        inc = res.scalar_one_or_none()
        if not inc:
            raise LookupError(f"Incident '{incident_id}' not found.")

        if not is_valid_state_transition(inc.status, target_status):
            raise ValueError(f"Illegal state transition from '{inc.status}' to '{target_status}'.")

        old_status = inc.status
        inc.status = target_status
        if notes:
            inc.notes = (inc.notes + "\n" + notes) if inc.notes else notes
        if analyst:
            inc.analyst = analyst

        if target_status == "TRIAGED" and not inc.triaged_at:
            inc.triaged_at = datetime.now(timezone.utc)
        elif target_status in ["RESOLVED", "CLOSED"]:
            inc.closed_at = datetime.now(timezone.utc)

        # Timeline event
        ev = IncidentTimelineEvent(
            incident_id=inc.id,
            event_type="STATUS_CHANGE",
            title=f"Status Transitioned: {old_status} -> {target_status}",
            description=notes or f"Status updated to {target_status} by {analyst or 'System'}.",
            actor=analyst or "SYSTEM",
            metadata_payload={"old_status": old_status, "new_status": target_status}
        )
        db.add(ev)
        await db.commit()
        await db.refresh(inc)
        return inc

    @staticmethod
    async def assign_analyst(
        incident_id: str,
        analyst_username: str,
        db: AsyncSession
    ) -> Incident:
        """Assigns an incident to a security analyst."""
        query = select(Incident).where(
            (Incident.id == incident_id) | (Incident.incident_code == incident_id)
        )
        res = await db.execute(query)
        inc = res.scalar_one_or_none()
        if not inc:
            raise LookupError(f"Incident '{incident_id}' not found.")

        inc.analyst = analyst_username
        ev = IncidentTimelineEvent(
            incident_id=inc.id,
            event_type="ANALYST_ACTION",
            title=f"Incident Assigned to {analyst_username}",
            description=f"Analyst {analyst_username} assigned to lead investigation.",
            actor=analyst_username,
            metadata_payload={"assigned_analyst": analyst_username}
        )
        db.add(ev)
        await db.commit()
        await db.refresh(inc)
        return inc

    @staticmethod
    async def resolve_incident(
        incident_id: str,
        resolution_notes: str,
        remediation_action: Optional[str],
        analyst: Optional[str],
        db: AsyncSession
    ) -> Incident:
        """Resolves an incident with resolution notes and containment details."""
        query = select(Incident).where(
            (Incident.id == incident_id) | (Incident.incident_code == incident_id)
        )
        res = await db.execute(query)
        inc = res.scalar_one_or_none()
        if not inc:
            raise LookupError(f"Incident '{incident_id}' not found.")

        inc.status = "RESOLVED"
        inc.resolution = resolution_notes
        if remediation_action:
            inc.remediation_action = remediation_action
        inc.closed_at = datetime.now(timezone.utc)

        ev = IncidentTimelineEvent(
            incident_id=inc.id,
            event_type="RESOLUTION",
            title="Incident Resolved",
            description=resolution_notes,
            actor=analyst or "ANALYST",
            metadata_payload={
                "remediation_action": remediation_action,
                "resolution": resolution_notes
            }
        )
        db.add(ev)
        await db.commit()
        await db.refresh(inc)
        return inc

    @staticmethod
    async def get_statistics(db: AsyncSession) -> Dict[str, Any]:
        """Calculates comprehensive operational incident statistics."""
        # Total counts by status
        res_status = await db.execute(
            select(Incident.status, func.count(Incident.id)).group_by(Incident.status)
        )
        status_counts = dict(res_status.all())

        # Total counts by severity
        res_sev = await db.execute(
            select(Incident.severity, func.count(Incident.id)).group_by(Incident.severity)
        )
        severity_counts = dict(res_sev.all())

        # Total counts by attack type
        res_att = await db.execute(
            select(Incident.attack_type, func.count(Incident.id))
            .group_by(Incident.attack_type)
            .order_by(desc(func.count(Incident.id)))
            .limit(10)
        )
        attack_type_counts = dict(res_att.all())

        # Total count
        total_inc = sum(status_counts.values())
        active_inc = sum(count for st, count in status_counts.items() if st in ["OPEN", "DETECTED", "TRIAGED", "INVESTIGATING"])

        # Average risk score
        res_avg_risk = await db.execute(select(func.avg(Incident.risk_score)))
        avg_risk = float(res_avg_risk.scalar() or 0.0)

        return {
            "total_incidents": total_inc,
            "active_incidents": active_inc,
            "average_risk_score": round(avg_risk, 2),
            "by_status": status_counts,
            "by_severity": severity_counts,
            "top_attack_types": attack_type_counts,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
