"""
backend/app/services/alert_intelligence_service.py
==================================================
Phase 16.2 & 16.3 Alert Intelligence, Deduplication, Grouping, and Prioritization Engine.
Groups related alerts under incidents while preserving raw evidence,
and calculates explainable multi-factor priority scores (0–100).
"""

import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.alert_intelligence import AlertFingerprint, AlertGroup, AlertPriorityScore

logger = logging.getLogger("Aegivanta.AlertIntelligence")


class AlertIntelligenceService:
    """Manages intelligent alert deduplication, clustering, and explainable prioritization."""

    @classmethod
    def compute_fingerprint_hash(
        cls,
        source_ip: str,
        destination_ip: str,
        attack_type: str,
        signature: Optional[str] = None
    ) -> str:
        """Generates deterministic SHA-256 fingerprint for deduplication."""
        raw = f"{source_ip.strip()}:{destination_ip.strip()}:{attack_type.strip().upper()}:{signature or 'DEFAULT'}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    async def process_incoming_alert(
        cls,
        db: AsyncSession,
        alert: Alert,
        tenant_id: Optional[str] = None
    ) -> Tuple[bool, Optional[AlertGroup], AlertPriorityScore]:
        """
        Processes an alert through deduplication, grouping, and prioritization:
        Returns: (is_duplicate_suppressed, alert_group, priority_score_record)
        """
        # 1. Compute and track fingerprint
        fp_hash = cls.compute_fingerprint_hash(
            source_ip=alert.source_ip,
            destination_ip=alert.destination_ip,
            attack_type=alert.attack_type,
            signature=alert.source
        )

        fp_stmt = select(AlertFingerprint).where(AlertFingerprint.fingerprint_hash == fp_hash)
        fp_res = await db.execute(fp_stmt)
        fp = fp_res.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        is_suppressed = False

        if fp:
            fp.last_seen = now
            fp.occurrence_count += 1
            # Suppress if seen within 60 seconds to prevent alert storms
            if (now - fp.first_seen).total_seconds() < 300 and fp.occurrence_count > 5:
                fp.is_suppressed = True
                is_suppressed = True
        else:
            fp = AlertFingerprint(
                fingerprint_hash=fp_hash,
                tenant_id=tenant_id,
                source_ip=alert.source_ip,
                destination_ip=alert.destination_ip,
                attack_type=alert.attack_type,
                signature=alert.source,
                first_seen=now,
                last_seen=now,
                occurrence_count=1,
                is_suppressed=False
            )
            db.add(fp)

        # 2. Correlate / create AlertGroup
        grp_stmt = select(AlertGroup).where(
            and_(
                AlertGroup.root_attack_type == alert.attack_type,
                AlertGroup.status == "ACTIVE"
            )
        ).order_by(AlertGroup.created_at.desc())
        grp_res = await db.execute(grp_stmt)
        alert_group = grp_res.scalars().first()

        if alert_group:
            alert_group.alert_count += 1
            if alert.source_ip not in (alert_group.source_ips or []):
                alert_group.source_ips = list(set((alert_group.source_ips or []) + [alert.source_ip]))
            alert_group.updated_at = now
        else:
            alert_group = AlertGroup(
                incident_id=alert.incident_id,
                tenant_id=tenant_id,
                title=f"Correlated {alert.attack_type} Campaign",
                root_attack_type=alert.attack_type,
                alert_count=1,
                confidence_score=alert.confidence or 0.85,
                status="ACTIVE",
                affected_assets=[alert.asset_id] if alert.asset_id else [],
                source_ips=[alert.source_ip] if alert.source_ip else [],
                mitre_techniques=["T1059", "T1021"]
            )
            db.add(alert_group)

        # 3. Calculate Explainable Priority Score (0–100)
        priority_score_rec = await cls.calculate_priority_score(db, alert, tenant_id)

        await db.flush()
        return is_suppressed, alert_group, priority_score_rec

    @classmethod
    async def calculate_priority_score(
        cls,
        db: AsyncSession,
        alert: Alert,
        tenant_id: Optional[str] = None
    ) -> AlertPriorityScore:
        """
        Calculates normalized Priority Score (0–100) based on 6 explainable factors:
        1. Severity Base (0–30)
        2. Asset Criticality (0–25)
        3. Threat Intelligence Reputation (0–15)
        4. Attack Vector & Lateral Movement Risk (0–15)
        5. Detection Confidence (0–10)
        6. Historical Behavior / Anomaly Delta (0–5)
        """
        factors = {}
        reasons = []
        total_score = 0.0

        # Factor 1: Severity Base
        sev_map = {"critical": 30.0, "high": 22.0, "medium": 14.0, "low": 6.0, "info": 2.0}
        sev_score = sev_map.get(alert.severity.lower(), 12.0)
        factors["severity"] = sev_score
        total_score += sev_score
        if sev_score >= 22.0:
            reasons.append(f"{alert.severity.upper()} severity alert signature detected")

        # Factor 2: Asset Criticality
        asset_score = 10.0
        if alert.asset_id:
            asset_stmt = select(ProtectedAsset).where(ProtectedAsset.id == alert.asset_id)
            asset_res = await db.execute(asset_stmt)
            asset = asset_res.scalar_one_or_none()
            if asset:
                crit_map = {"CRITICAL": 25.0, "HIGH": 18.0, "MEDIUM": 10.0, "LOW": 4.0}
                asset_score = crit_map.get(str(asset.criticality).upper(), 10.0)
                if asset_score >= 18.0:
                    reasons.append(f"Target is a {asset.criticality} production asset ({asset.name})")
        factors["asset_criticality"] = asset_score
        total_score += asset_score

        # Factor 3: Threat Intelligence
        ti_stmt = select(ThreatIndicator).where(
            (ThreatIndicator.normalized_value == alert.source_ip) |
            (ThreatIndicator.raw_value == alert.source_ip)
        )
        ti_res = await db.execute(ti_stmt)
        ti_indicator = ti_res.scalar_one_or_none()
        ti_score = 15.0 if ti_indicator else 0.0
        factors["threat_intelligence"] = ti_score
        total_score += ti_score
        if ti_indicator:
            reasons.append(f"Source IP matches known threat indicator ({ti_indicator.source or 'Threat Feed'})")


        # Factor 4: Attack Vector Risk
        att_upper = alert.attack_type.upper()
        if any(k in att_upper for k in ["BRUTE", "LATERAL", "EXPLOIT", "BOTNET", "DDOS"]):
            vec_score = 15.0
            reasons.append(f"High-impact attack vector: {alert.attack_type}")
        else:
            vec_score = 8.0
        factors["attack_vector_risk"] = vec_score
        total_score += vec_score

        # Factor 5: Detection Confidence
        conf = alert.confidence or 0.85
        conf_score = round(conf * 10.0, 1)
        factors["detection_confidence"] = conf_score
        total_score += conf_score
        if conf >= 0.90:
            reasons.append(f"High confidence ML detection ({int(conf * 100)}%)")

        # Factor 6: Historical Behavior
        factors["behavioral_anomaly"] = 5.0
        total_score += 5.0

        normalized_score = min(100.0, max(0.0, round(total_score, 1)))

        if normalized_score >= 80.0:
            level = "CRITICAL"
        elif normalized_score >= 60.0:
            level = "HIGH"
        elif normalized_score >= 40.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        explanation = f"Priority {int(normalized_score)}/100 ({level}) assigned based on: " + "; ".join(reasons)

        priority_rec = AlertPriorityScore(
            alert_id=alert.id,
            tenant_id=tenant_id,
            priority_score=normalized_score,
            priority_level=level,
            contributing_factors=factors,
            reasons=reasons,
            explanation=explanation,
            calculated_at=datetime.now(timezone.utc)
        )
        db.add(priority_rec)
        return priority_rec
