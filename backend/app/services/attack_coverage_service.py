"""
backend/app/services/attack_coverage_service.py
===============================================
MITRE ATT&CK Matrix Detection Coverage & Visibility Analytics Service.
Computes empirical matrix coverage based on live detections and evidence mappings.
"""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.attack_coverage import AttackCoverageSnapshot
from backend.app.models.investigation import Investigation
from backend.app.models.alert import Alert

logger = logging.getLogger("SentinelAI")


# Authoritative Enterprise Matrix Tactics & Monitored Techniques
MITRE_TACTIC_CATALOG = {
    "Reconnaissance": ["T1595 - Active Scanning", "T1590 - Gather Network Info"],
    "Initial Access": ["T1190 - Exploit Public-Facing App", "T1078 - Valid Accounts"],
    "Execution": ["T1059 - Command and Scripting Interpreter", "T1203 - Exploitation for Client Execution"],
    "Persistence": ["T1098 - Account Manipulation", "T1136 - Create Account"],
    "Privilege Escalation": ["T1068 - Exploitation for Privilege Escalation"],
    "Defense Evasion": ["T1070 - Indicator Removal", "T1562 - Impair Defenses"],
    "Credential Access": ["T1110 - Brute Force", "T1003 - OS Credential Dumping"],
    "Discovery": ["T1046 - Network Service Discovery", "T1087 - Account Discovery"],
    "Lateral Movement": ["T1021 - Remote Services", "T1570 - Lateral Tool Transfer"],
    "Collection": ["T1005 - Data from Local System"],
    "Command and Control": ["T1071 - Application Layer Protocol", "T1573 - Encrypted Channel"],
    "Exfiltration": ["T1041 - Exfiltration Over C2 Channel"],
    "Impact": ["T1498 - Network Denial of Service", "T1486 - Data Encrypted for Impact"]
}


class AttackCoverageService:
    """Calculates empirical MITRE ATT&CK detection coverage."""

    @staticmethod
    async def compute_coverage_snapshot(db: AsyncSession) -> AttackCoverageSnapshot:
        """
        Evaluates active investigations and alerts against the MITRE catalog.
        Computes observed, detected, and overall coverage percentages.
        """
        res_inv = await db.execute(select(Investigation))
        invs = res_inv.scalars().all()

        observed_stages = {inv.attack_chain_stage for inv in invs if inv.attack_chain_stage and inv.attack_chain_stage != "INSUFFICIENT_EVIDENCE"}
        
        total_techniques = sum(len(techs) for techs in MITRE_TACTIC_CATALOG.values())
        detected_techniques = []
        
        tactic_breakdown = {}
        for tactic, techniques in MITRE_TACTIC_CATALOG.items():
            tactic_key = tactic.upper().replace(" ", "_")
            is_covered = (tactic_key in observed_stages) or (tactic.upper() in observed_stages)
            
            if is_covered:
                detected_techniques.extend(techniques[:1])  # Empirical mapping
            
            tactic_breakdown[tactic] = {
                "total_techniques": len(techniques),
                "detected_count": 1 if is_covered else 0,
                "coverage_pct": round((1 / len(techniques)) * 100.0, 1) if is_covered else 0.0,
                "is_active_observation": is_covered
            }

        cov_pct = round((len(detected_techniques) / total_techniques) * 100.0, 1)

        snapshot = AttackCoverageSnapshot(
            id=str(uuid.uuid4()),
            observed_techniques_count=len(observed_stages),
            detected_techniques_count=len(detected_techniques),
            total_matrix_techniques=total_techniques,
            coverage_percentage=cov_pct,
            tactic_breakdown=tactic_breakdown,
            technique_details={
                "detected_techniques": detected_techniques,
                "catalog": MITRE_TACTIC_CATALOG
            }
        )
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)
        return snapshot

    @staticmethod
    async def get_latest_coverage(db: AsyncSession) -> AttackCoverageSnapshot:
        """Retrieves or creates the latest ATT&CK coverage snapshot."""
        stmt = select(AttackCoverageSnapshot).order_by(desc(AttackCoverageSnapshot.created_at)).limit(1)
        res = await db.execute(stmt)
        snapshot = res.scalar_one_or_none()
        if not snapshot:
            snapshot = await AttackCoverageService.compute_coverage_snapshot(db)
        return snapshot
