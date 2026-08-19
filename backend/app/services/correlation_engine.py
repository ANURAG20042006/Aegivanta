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
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.logging import logger
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.services.risk_engine import RiskScoringEngine


CORRELATION_WINDOW_SECONDS = 300  # 5 minutes


# Authoritative MITRE ATT&CK Mapping Catalog
MITRE_ATTACK_MAPPINGS = {
    "Port Scan": {"tactic": "Discovery", "technique_id": "T1046", "technique_name": "Network Service Discovery"},
    "SSH-Patator": {"tactic": "Credential Access", "technique_id": "T1110", "technique_name": "Brute Force"},
    "FTP-Patator": {"tactic": "Credential Access", "technique_id": "T1110", "technique_name": "Brute Force"},
    "Brute Force": {"tactic": "Credential Access", "technique_id": "T1110", "technique_name": "Brute Force"},
    "SQL Injection": {"tactic": "Initial Access", "technique_id": "T1190", "technique_name": "Exploit Public-Facing Application"},
    "XSS": {"tactic": "Initial Access", "technique_id": "T1190", "technique_name": "Exploit Public-Facing Application"},
    "Malware": {"tactic": "Command and Control", "technique_id": "T1071", "technique_name": "Application Layer Protocol"},
    "Botnet": {"tactic": "Command and Control", "technique_id": "T1071", "technique_name": "Application Layer Protocol"},
    "Data Exfiltration": {"tactic": "Exfiltration", "technique_id": "T1041", "technique_name": "Exfiltration Over C2 Channel"},
    "DDoS": {"tactic": "Impact", "technique_id": "T1498", "technique_name": "Network Denial of Service"},
    "DoS Hulk": {"tactic": "Impact", "technique_id": "T1498", "technique_name": "Network Denial of Service"},
    "DoS GoldenEye": {"tactic": "Impact", "technique_id": "T1498", "technique_name": "Network Denial of Service"},
    "DoS Slowloris": {"tactic": "Impact", "technique_id": "T1498", "technique_name": "Network Denial of Service"},
    "ARP Spoofing": {"tactic": "Defense Evasion", "technique_id": "T1557", "technique_name": "Adversary-in-the-Middle"},
    "DNS Spoofing": {"tactic": "Defense Evasion", "technique_id": "T1557", "technique_name": "Adversary-in-the-Middle"},
    "Ransomware": {"tactic": "Impact", "technique_id": "T1486", "technique_name": "Data Encrypted for Impact"}
}


class IncidentCorrelationEngine:
    """
    Correlates security alerts deterministically into managed incidents
    and maintains chronological attack timelines with MITRE ATT&CK progression.
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
    def get_mitre_mapping(cls, attack_type: str) -> Dict[str, str]:
        """Resolves MITRE ATT&CK tactic and technique for a given attack classification."""
        return MITRE_ATTACK_MAPPINGS.get(
            attack_type,
            {"tactic": "Impact", "technique_id": "T1498", "technique_name": "Network Denial of Service"}
        )

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
        Correlates an incoming Alert with an existing active Incident or creates a new Incident.
        Returns: (incident, timeline_event)
        """
        window_start = alert.timestamp - timedelta(seconds=CORRELATION_WINDOW_SECONDS)
        asset_crit = asset.criticality if asset else "medium"
        mitre_info = cls.get_mitre_mapping(alert.attack_type)

        # Search for active incident matching correlation criteria
        # Match criteria: Same destination_ip/asset OR same source_ip, within time window, NOT resolved/closed
        active_statuses = ["DETECTED", "TRIAGED", "INVESTIGATING", "CONTAINED"]
        
        stmt = (
            select(Incident)
            .where(
                and_(
                    Incident.status.in_(active_statuses),
                    Incident.last_seen >= window_start,
                    or_(
                        and_(Incident.asset_id.isnot(None), Incident.asset_id == alert.asset_id),
                        and_(Incident.destination_ip.isnot(None), Incident.destination_ip == alert.destination_ip)
                    ),
                    or_(
                        and_(Incident.source_ip.isnot(None), Incident.source_ip == alert.source_ip),
                        Incident.attack_type == alert.attack_type
                    )
                )
            )
            .order_by(Incident.last_seen.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        existing_incident = result.scalar_one_or_none()

        if existing_incident:
            # 1. Correlate with existing active incident
            existing_incident.alert_count += 1
            existing_incident.last_seen = alert.timestamp

            # Deterministic confidence aggregation: incorporate incoming alert's confidence
            incoming_conf = float(alert.confidence) if alert.confidence is not None else 0.0
            current_conf = float(existing_incident.confidence_score) if existing_incident.confidence_score is not None else 0.0
            aggregated_confidence = max(current_conf, incoming_conf)
            existing_incident.confidence_score = aggregated_confidence

            # Compute preliminary severity
            preliminary_severity = cls.determine_incident_severity(
                current_severity=existing_incident.severity,
                incoming_alert_severity=alert.severity,
                updated_risk_score=existing_incident.risk_score
            )

            # Calculate updated risk score directly incorporating incoming alert confidence & severity
            updated_risk = RiskScoringEngine.calculate_risk_score(
                severity=preliminary_severity,
                confidence=aggregated_confidence,
                criticality=asset_crit,
                alert_count=existing_incident.alert_count
            )
            existing_incident.risk_score = updated_risk

            # Finalize severity based on newly calculated risk score
            existing_incident.severity = cls.determine_incident_severity(
                current_severity=preliminary_severity,
                incoming_alert_severity=alert.severity,
                updated_risk_score=updated_risk
            )
            
            alert.incident_id = existing_incident.id
            
            # Create chronological timeline event
            timeline_event = IncidentTimelineEvent(
                incident_id=existing_incident.id,
                timestamp=alert.timestamp,
                event_type="ALERT_CORRELATED",
                title=f"Correlated Alert: {alert.alert_id}",
                description=f"Correlated {alert.severity.upper()} {alert.attack_type} attack flow from {alert.source_ip} (Total alerts: {existing_incident.alert_count}, Incident Severity: {existing_incident.severity}, MITRE: {mitre_info['tactic']} [{mitre_info['technique_id']}])",
                actor="CORRELATION_ENGINE",
                metadata_payload={
                    "alert_id": alert.alert_id,
                    "severity": alert.severity,
                    "confidence": alert.confidence,
                    "risk_score": alert.risk_score,
                    "mitre_tactic": mitre_info["tactic"],
                    "mitre_technique_id": mitre_info["technique_id"],
                    "mitre_technique_name": mitre_info["technique_name"]
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
                description=f"Automated security incident initiated by ML threat detection ({alert.attack_type}) from {alert.source_ip}. MITRE Tactic: {mitre_info['tactic']} ({mitre_info['technique_id']}).",
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
                description=f"Initial {alert.severity.upper()} {alert.attack_type} threat detected by {alert.source}. MITRE Tactic: {mitre_info['tactic']} [{mitre_info['technique_id']}].",
                actor="CORRELATION_ENGINE",
                metadata_payload={
                    "initial_alert_id": alert.alert_id,
                    "source_ip": alert.source_ip,
                    "destination_ip": alert.destination_ip,
                    "severity": alert.severity,
                    "confidence": alert.confidence,
                    "risk_score": alert.risk_score,
                    "mitre_tactic": mitre_info["tactic"],
                    "mitre_technique_id": mitre_info["technique_id"],
                    "mitre_technique_name": mitre_info["technique_name"]
                }
            )
            db.add(timeline_event)
            target_incident = new_incident
            logger.info("Initiated new incident %s from alert %s", incident_code, alert.alert_id)

        # Update Asset risk score and last_seen timestamp if associated
        if asset:
            asset.last_seen = alert.timestamp
            asset.risk_score = max(asset.risk_score, target_incident.risk_score)
            if target_incident.risk_score >= 75.0:
                asset.status = "compromised"
            elif target_incident.risk_score >= 50.0 and asset.status == "active":
                asset.status = "degraded"
                
        return target_incident, timeline_event
