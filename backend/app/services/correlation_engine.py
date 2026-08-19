"""
backend/app/services/correlation_engine.py
==========================================
Deterministic, Rule-Based Incident Correlation & Attack Timeline Engine.

Correlates incoming alerts into unified security incidents based on:
1. Protected Asset ID / Destination IP matching
2. Threat Actor Source IP matching
3. Attack Category matching
4. Configurable time window (default 300 seconds)
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.logging import logger
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.services.risk_engine import RiskScoringEngine


CORRELATION_WINDOW_SECONDS = 300  # 5 minutes


class IncidentCorrelationEngine:
    """
    Correlates security alerts deterministically into managed incidents
    and maintains chronological attack timelines.
    """

    SEVERITY_HIERARCHY = {
        "INFO": 0,
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }
    SEVERITY_NAMES = {0: "Info", 1: "Low", 2: "Medium", 3: "High", 4: "Critical"}

    @classmethod
    def determine_incident_severity(
        cls,
        current_severity: str,
        incoming_alert_severity: str,
        updated_risk_score: float
    ) -> str:
        """
        Explicit Incident Severity Policy combining:
        1. Alert Severity: Elevates if incoming alert severity is higher.
        2. Accumulated Risk Score: Elevates if multi-factor risk score crosses operational thresholds:
           - Risk >= 80.0 -> Critical (Level 4)
           - Risk >= 60.0 -> High (Level 3)
           - Risk >= 40.0 -> Medium (Level 2)
        3. Monotonic Protection: Never downgrades an active incident's severity during correlation.
        """
        curr_lvl = cls.SEVERITY_HIERARCHY.get(current_severity.upper(), 1)
        alert_lvl = cls.SEVERITY_HIERARCHY.get(incoming_alert_severity.upper(), 1)

        if updated_risk_score >= 80.0:
            risk_lvl = 4
        elif updated_risk_score >= 60.0:
            risk_lvl = 3
        elif updated_risk_score >= 40.0:
            risk_lvl = 2
        else:
            risk_lvl = 1

        final_lvl = max(curr_lvl, alert_lvl, risk_lvl)
        return cls.SEVERITY_NAMES.get(final_lvl, "Medium")

    @classmethod
    async def process_alert(
        cls,
        db: AsyncSession,
        alert: Alert,
        asset: Optional[ProtectedAsset] = None
    ) -> Tuple[Incident, IncidentTimelineEvent]:
        """
        Ingests a new Alert, correlates with active incidents or creates a new incident,
        appends a timeline event, updates asset risk, and persists state.
        """
        now = datetime.now(timezone.utc)
        window_start = alert.timestamp - timedelta(seconds=CORRELATION_WINDOW_SECONDS)
        
        # Search for active candidate incident within correlation time window
        stmt = (
            select(Incident)
            .where(
                and_(
                    Incident.status.in_(["DETECTED", "TRIAGED", "INVESTIGATING"]),
                    Incident.last_seen >= window_start,
                    or_(
                        and_(Incident.asset_id.isnot(None), Incident.asset_id == alert.asset_id),
                        Incident.destination_ip == alert.destination_ip
                    ),
                    or_(
                        Incident.source_ip == alert.source_ip,
                        Incident.attack_type == alert.attack_type
                    )
                )
            )
            .order_by(Incident.last_seen.desc())
            .limit(1)
        )
        
        result = await db.execute(stmt)
        existing_incident = result.scalar_one_or_none()
        
        asset_crit = asset.criticality if asset else "medium"
        
        if existing_incident:
            # 1. Correlate with existing active incident
            existing_incident.alert_count += 1
            existing_incident.last_seen = alert.timestamp

            # Deterministic confidence aggregation: track highest observed confidence across alerts
            if alert.confidence is not None:
                if existing_incident.confidence_score is not None:
                    existing_incident.confidence_score = max(existing_incident.confidence_score, alert.confidence)
                else:
                    existing_incident.confidence_score = alert.confidence

            # Apply explicit Incident Severity Policy
            existing_incident.severity = cls.determine_incident_severity(
                current_severity=existing_incident.severity,
                incoming_alert_severity=alert.severity,
                updated_risk_score=existing_incident.risk_score
            )

            # Calculate updated risk score from real accumulated evidence
            updated_risk = RiskScoringEngine.calculate_risk_score(
                severity=existing_incident.severity,
                confidence=existing_incident.confidence_score,
                criticality=asset_crit,
                alert_count=existing_incident.alert_count
            )
            existing_incident.risk_score = updated_risk
            
            alert.incident_id = existing_incident.id
            
            # Create chronological timeline event
            timeline_event = IncidentTimelineEvent(
                incident_id=existing_incident.id,
                timestamp=alert.timestamp,
                event_type="ALERT_CORRELATED",
                title=f"Correlated Alert: {alert.alert_id}",
                description=f"Correlated {alert.severity.upper()} {alert.attack_type} attack flow from {alert.source_ip} (Total alerts: {existing_incident.alert_count}, Incident Severity: {existing_incident.severity})",
                actor="CORRELATION_ENGINE",
                metadata_payload={
                    "alert_id": alert.alert_id,
                    "severity": alert.severity,
                    "confidence": alert.confidence,
                    "risk_score": alert.risk_score
                }
            )
            db.add(timeline_event)
            target_incident = existing_incident
            logger.info("Correlated alert %s to active incident %s (Total alerts: %d)", alert.alert_id, existing_incident.incident_code, existing_incident.alert_count)
            
        else:
            # 2. Create new incident from this alert with real telemetry & model metadata
            incident_code = f"INC-{uuid.uuid4().hex[:8].upper()}"
            title = f"Potential {alert.attack_type} Activity against {asset.name if asset else alert.destination_ip}"
            
            actual_model = alert.source.replace("ML_ENGINE:", "") if alert.source.startswith("ML_ENGINE:") else alert.source
            actual_version = f"{actual_model.lower().replace(' ', '_')}-v1.0"
            
            new_incident = Incident(
                incident_code=incident_code,
                alert_id=alert.alert_id,
                asset_id=alert.asset_id,
                title=title,
                description=f"Automated security incident initiated by ML threat detection ({alert.attack_type}) from {alert.source_ip}.",
                status="DETECTED",
                risk_score=alert.risk_score,
                alert_count=1,
                source_ip=alert.source_ip,
                destination_ip=alert.destination_ip,
                source_port=alert.source_port or 0,
                destination_port=alert.destination_port or 0,
                protocol=alert.protocol or "TCP",
                packet_length=alert.packet_length if (hasattr(alert, "packet_length") and alert.packet_length is not None) else 0,
                flow_duration=alert.flow_duration if (hasattr(alert, "flow_duration") and alert.flow_duration is not None) else 0.0,
                attack_type=alert.attack_type,
                confidence_score=alert.confidence,
                is_malicious=True,
                severity=alert.severity.capitalize(),
                model_name=actual_model,
                model_version=actual_version,
                timestamp=alert.timestamp,
                first_seen=alert.timestamp,
                last_seen=alert.timestamp
            )
            db.add(new_incident)
            await db.flush()  # Obtain new_incident.id
            
            alert.incident_id = new_incident.id
            
            # Root timeline event
            timeline_event = IncidentTimelineEvent(
                incident_id=new_incident.id,
                timestamp=alert.timestamp,
                event_type="DETECTION",
                title=f"Incident Initiated: {incident_code}",
                description=f"Initial {alert.severity.upper()} {alert.attack_type} threat detected by {alert.source}.",
                actor="CORRELATION_ENGINE",
                metadata_payload={
                    "initial_alert_id": alert.alert_id,
                    "source_ip": alert.source_ip,
                    "destination_ip": alert.destination_ip,
                    "confidence": alert.confidence
                }
            )
            db.add(timeline_event)
            target_incident = new_incident
            logger.info("Created new incident %s from alert %s", incident_code, alert.alert_id)

        # Update Asset risk score and last_seen timestamp if associated
        if asset:
            asset.last_seen = alert.timestamp
            asset.risk_score = max(asset.risk_score, target_incident.risk_score)
            if target_incident.risk_score >= 75.0:
                asset.status = "compromised"
            elif target_incident.risk_score >= 50.0 and asset.status == "active":
                asset.status = "degraded"
                
        return target_incident, timeline_event
