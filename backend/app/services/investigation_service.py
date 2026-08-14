"""
backend/app/services/investigation_service.py
=============================================
Automated Incident Investigation, Evidence Aggregation,
and Empirical MITRE ATT&CK Stage Mapping Service.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.behavioral import AnomalyEvent
from backend.app.models.investigation import Investigation, InvestigationEvidence
from backend.app.core.logging import logger


# Empirical MITRE ATT&CK Tactical Rules
ATTACK_TACTIC_RULES = {
    "PortScan": {"stage": "RECONNAISSANCE", "tactic_id": "TA0043", "technique": "Network Service Scanning (T1046)", "base_conf": 0.90},
    "Bot": {"stage": "RECONNAISSANCE", "tactic_id": "TA0043", "technique": "Active Scanning / Automated Probe (T1595)", "base_conf": 0.85},
    "FTP-Patator": {"stage": "INITIAL_ACCESS", "tactic_id": "TA0001", "technique": "Brute Force / Password Guessing (T1110)", "base_conf": 0.92},
    "SSH-Patator": {"stage": "INITIAL_ACCESS", "tactic_id": "TA0001", "technique": "Brute Force / SSH Auth (T1110.001)", "base_conf": 0.92},
    "Web Attack \u2013 Brute Force": {"stage": "INITIAL_ACCESS", "tactic_id": "TA0001", "technique": "Password Spraying / Credential Stuffing (T1110.003)", "base_conf": 0.88},
    "Web Attack \u2013 XSS": {"stage": "EXECUTION", "tactic_id": "TA0002", "technique": "Cross-Site Scripting (T1059.007)", "base_conf": 0.91},
    "Web Attack \u2013 Sql Injection": {"stage": "EXECUTION", "tactic_id": "TA0002", "technique": "Exploit Public-Facing Application / SQLi (T1190)", "base_conf": 0.94},
    "Infiltration": {"stage": "LATERAL_MOVEMENT", "tactic_id": "TA0008", "technique": "Lateral Tool Transfer & Propagation (T1570)", "base_conf": 0.87},
    "Heartbleed": {"stage": "EXFILTRATION", "tactic_id": "TA0010", "technique": "Exploitation for Data Exfiltration (T1048)", "base_conf": 0.95},
    "DoS/DDoS": {"stage": "IMPACT", "tactic_id": "TA0040", "technique": "Network Denial of Service (T1498)", "base_conf": 0.93},
    "DoS Hulk": {"stage": "IMPACT", "tactic_id": "TA0040", "technique": "Direct Network Flooding (T1498.001)", "base_conf": 0.93},
    "DoS GoldenEye": {"stage": "IMPACT", "tactic_id": "TA0040", "technique": "Application Exhaustion Flood (T1499.003)", "base_conf": 0.93},
    "DoS slowloris": {"stage": "IMPACT", "tactic_id": "TA0040", "technique": "Slowloris Connection Exhaustion (T1499.001)", "base_conf": 0.92},
    "DoS Slowhttptest": {"stage": "IMPACT", "tactic_id": "TA0040", "technique": "Slow HTTP Exhaustion (T1499.001)", "base_conf": 0.92},
    "DDoS": {"stage": "IMPACT", "tactic_id": "TA0040", "technique": "Endpoint Denial of Service (T1499)", "base_conf": 0.94},
    "DoS_Service_Outage": {"stage": "IMPACT", "tactic_id": "TA0040", "technique": "Service Unavailable Outage (T1489)", "base_conf": 0.90}
}


def evaluate_attack_chain_stage(
    attack_type: Optional[str],
    alerts_count: int,
    ioc_matches_count: int,
    anomaly_count: int,
    risk_score: float
) -> Tuple[str, float, str, Dict[str, Any]]:
    """
    Evidence -> Rule -> ATT&CK Mapping -> Confidence -> Supporting Evidence.
    Never invents a stage without empirical evidence. Defaults to INSUFFICIENT_EVIDENCE.
    """
    if not attack_type or attack_type.upper() in ["BENIGN", "UNKNOWN", "NONE"] or alerts_count == 0:
        return (
            "INSUFFICIENT_EVIDENCE",
            0.30,
            "Insufficient empirical telemetry evidence to attribute a specific MITRE ATT&CK tactical stage.",
            {"evidence_basis": "NO_MALICIOUS_TELEMETRY"}
        )

    rule = ATTACK_TACTIC_RULES.get(attack_type)
    if not rule:
        return (
            "UNKNOWN",
            0.40,
            f"Unmapped attack classification '{attack_type}'. Insufficient signature evidence for MITRE ATT&CK taxonomy.",
            {"evidence_basis": "UNMAPPED_SIGNATURE"}
        )

    stage = rule["stage"]
    base_conf = rule["base_conf"]

    # Boost/adjust confidence based on corroborated multi-signal evidence
    corroboration_points = 0
    if ioc_matches_count > 0:
        corroboration_points += 0.05
    if anomaly_count > 0:
        corroboration_points += 0.03
    if alerts_count >= 3:
        corroboration_points += 0.02

    final_confidence = min(0.99, round(base_conf + corroboration_points, 2))

    summary = (
        f"Empirical evidence attributes this incident to MITRE ATT&CK Stage [{stage}] "
        f"via technique '{rule['technique']}' (Tactic: {rule['tactic_id']}). "
        f"Evidence corroborated by {alerts_count} alert(s), {ioc_matches_count} IOC hit(s), "
        f"and {anomaly_count} behavioral anomaly event(s)."
    )

    details = {
        "tactic_id": rule["tactic_id"],
        "technique": rule["technique"],
        "stage": stage,
        "base_confidence": base_conf,
        "corroboration_points": round(corroboration_points, 2),
        "total_evidence_signals": alerts_count + ioc_matches_count + anomaly_count
    }

    return stage, final_confidence, summary, details


class InvestigationService:
    """Core Automated Incident Investigation & Evidence Aggregation Engine."""

    @staticmethod
    async def analyze_incident(incident_id: str, db: AsyncSession) -> Optional[Investigation]:
        """
        Gathers evidence across alerts, flow telemetry, IOC matches, and anomalies
        to construct a deterministic, traceable incident investigation summary.
        """
        # 1. Query Incident
        res_inc = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = res_inc.scalar_one_or_none()
        if not incident:
            return None

        # 2. Query Associated Alerts
        res_alerts = await db.execute(select(Alert).where(Alert.incident_id == incident_id))
        alerts = res_alerts.scalars().all()

        # 3. Check for IOC Matches on Source/Destination IPs
        ip_addresses = {incident.source_ip, incident.destination_ip}
        for a in alerts:
            if a.source_ip:
                ip_addresses.add(a.source_ip)
            if a.destination_ip:
                ip_addresses.add(a.destination_ip)
        ip_addresses.discard(None)
        ip_addresses.discard("")

        ioc_matches = []
        if ip_addresses:
            res_iocs = await db.execute(select(ThreatIndicator).where(
                ThreatIndicator.normalized_value.in_(list(ip_addresses)),
                ThreatIndicator.is_active == True
            ))
            ioc_matches = res_iocs.scalars().all()

        # 4. Check for Behavioral Anomalies on Asset
        anomalies = []
        if incident.asset_id:
            res_anom = await db.execute(select(AnomalyEvent).where(
                AnomalyEvent.asset_id == incident.asset_id
            ).limit(5))
            anomalies = res_anom.scalars().all()

        # 5. Determine MITRE ATT&CK Stage via Evidence-Based Rule Evaluation
        attack_type = incident.attack_type or "Unknown"
        attack_stage, confidence_score, stage_explanation, stage_details = evaluate_attack_chain_stage(
            attack_type=attack_type,
            alerts_count=len(alerts),
            ioc_matches_count=len(ioc_matches),
            anomaly_count=len(anomalies),
            risk_score=incident.risk_score
        )

        # 6. Generate Traceable Findings & Deterministic Recommendations
        findings = {
            "incident_code": incident.incident_code,
            "total_alerts": len(alerts),
            "primary_threat": attack_type,
            "source_ip": incident.source_ip,
            "destination_ip": incident.destination_ip,
            "risk_score": incident.risk_score,
            "ioc_hits_count": len(ioc_matches),
            "anomaly_events_count": len(anomalies),
            "attack_stage_details": stage_details
        }

        recommendations = [
            f"Review perimeter firewall rules and connection tables for source IP {incident.source_ip}.",
            f"Inspect system health and error telemetry for protected asset {incident.asset_id or 'target'}."
        ]
        if ioc_matches:
            recommendations.append(f"Execute IP containment playbook for known malicious indicator {ioc_matches[0].normalized_value}.")
        if incident.risk_score >= 70:
            recommendations.append("High operational risk score detected (>70.0) — elevate incident priority to Tier-2 SOC review.")

        summary_text = (
            f"Automated investigation for incident {incident.incident_code or incident.id}: "
            f"Detected {len(alerts)} correlated alert(s) classified as '{attack_type}' "
            f"with operational risk score {incident.risk_score:.1f}/100. "
            f"{stage_explanation}"
        )

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # 7. Upsert Investigation Record
        res_inv = await db.execute(select(Investigation).where(Investigation.incident_id == incident_id))
        investigation = res_inv.scalar_one_or_none()

        if not investigation:
            investigation = Investigation(
                incident_id=incident_id,
                asset_id=incident.asset_id,
                status="COMPLETED",
                summary=summary_text,
                findings=findings,
                attack_chain_stage=attack_stage,
                confidence_score=confidence_score,
                recommended_actions=recommendations,
                created_at=now,
                updated_at=now
            )
            db.add(investigation)
            await db.flush()
        else:
            investigation.summary = summary_text
            investigation.findings = findings
            investigation.attack_chain_stage = attack_stage
            investigation.confidence_score = confidence_score
            investigation.recommended_actions = recommendations
            investigation.updated_at = now
            await db.flush()

        # 8. Create Traceable InvestigationEvidence Entries
        # Evidence: Alerts
        for a in alerts[:5]:
            db.add(InvestigationEvidence(
                investigation_id=investigation.id,
                evidence_type="ALERT",
                reference_id=a.id,
                description=f"Correlated Alert {a.id} ({a.attack_type}, severity: {a.severity})",
                timestamp=a.created_at,
                metadata_json={"alert_id": a.id, "risk_score": a.risk_score}
            ))

        # Evidence: IOC Matches
        for ioc in ioc_matches:
            db.add(InvestigationEvidence(
                investigation_id=investigation.id,
                evidence_type="IOC_MATCH",
                reference_id=ioc.id,
                description=f"Threat Intelligence IOC match: {ioc.normalized_value} ({ioc.threat_type}, source: {ioc.source})",
                timestamp=ioc.last_seen,
                metadata_json={"ioc_id": ioc.id, "confidence": ioc.confidence}
            ))

        # Evidence: Anomalies
        for anom in anomalies[:3]:
            db.add(InvestigationEvidence(
                investigation_id=investigation.id,
                evidence_type="BEHAVIORAL_ANOMALY",
                reference_id=anom.id,
                description=f"Behavioral Anomaly: {anom.explanation}",
                timestamp=anom.timestamp,
                metadata_json={"metric": anom.metric_name, "z_score": anom.z_score}
            ))

        await db.flush()

        # Broadcast WebSocket telemetry
        try:
            from backend.app.api.v1.websocket import manager
            await manager.broadcast({
                "type": "INVESTIGATION_UPDATE",
                "data": {
                    "investigation_id": investigation.id,
                    "incident_id": incident_id,
                    "attack_chain_stage": attack_stage,
                    "confidence_score": confidence_score,
                    "summary": summary_text,
                    "recommended_actions": recommendations,
                    "timestamp": now.isoformat()
                }
            })
        except Exception:
            pass

        return investigation
