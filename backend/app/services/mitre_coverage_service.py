"""
backend/app/services/mitre_coverage_service.py
==============================================
Phase 3.6 MITRE ATT&CK Detection Coverage Analytics Service.
Computes real-time coverage analytics against the MITRE Enterprise ATT&CK matrix based on
active detection rules, telemetry events, and correlated incident evidence.
"""

from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.detection.rules.production_rules import detection_registry
from backend.app.models.incident import Incident

MITRE_ENTERPRISE_CATALOG = {
    "T1110.001": {"name": "Password Guessing", "tactic": "Credential Access"},
    "T1110.003": {"name": "Password Spraying", "tactic": "Credential Access"},
    "T1078.004": {"name": "Cloud Accounts", "tactic": "Defense Evasion / Initial Access"},
    "T1078.001": {"name": "Default / Database Accounts", "tactic": "Persistence"},
    "T1078":     {"name": "Valid Accounts", "tactic": "Defense Evasion / Privilege Escalation"},
    "T1071.001": {"name": "Web Protocols (HTTP/HTTPS)", "tactic": "Command and Control"},
    "T1566":     {"name": "Phishing", "tactic": "Initial Access"},
    "T1021.002": {"name": "SMB / Windows Admin Shares", "tactic": "Lateral Movement"},
    "T1021.001": {"name": "Remote Desktop Protocol (RDP)", "tactic": "Lateral Movement"},
    "T1021.004": {"name": "SSH Remote Services", "tactic": "Lateral Movement"},
    "T1021.006": {"name": "Windows Remote Management (WinRM)", "tactic": "Lateral Movement"},
    "T1021":     {"name": "Remote Services", "tactic": "Lateral Movement"},
    "T1047":     {"name": "Windows Management Instrumentation (WMI)", "tactic": "Execution"},
    "T1570":     {"name": "Lateral Tool Transfer", "tactic": "Lateral Movement"},
    "T1087":     {"name": "Account Discovery", "tactic": "Discovery"},
    "T1087.002": {"name": "Domain Account Discovery", "tactic": "Discovery"},
    "T1048":     {"name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration"},
    "T1041":     {"name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration"},
    "T1558":     {"name": "Steal or Forge Kerberos Tickets", "tactic": "Credential Access"},
    "T1046":     {"name": "Network Service Discovery", "tactic": "Discovery"},
    "T1595.001": {"name": "Active Scanning: Scanning IP Blocks", "tactic": "Reconnaissance"},
    "T1498":     {"name": "Network Denial of Service", "tactic": "Impact"},
    "T1499":     {"name": "Endpoint Denial of Service", "tactic": "Impact"},
    "T1059.001": {"name": "PowerShell Execution", "tactic": "Execution"},
    "T1059.003": {"name": "Windows Command Shell", "tactic": "Execution"}
}


class MitreCoverageService:
    """Computes evidence-backed MITRE ATT&CK coverage analytics."""

    @classmethod
    def get_coverage_summary(cls) -> Dict[str, Any]:
        """Synchronous summary of MITRE catalog techniques."""
        return {
            "total_catalog_techniques": len(MITRE_ENTERPRISE_CATALOG),
            "catalog": [
                {"technique_id": k, "name": v["name"], "tactic": v["tactic"]}
                for k, v in MITRE_ENTERPRISE_CATALOG.items()
            ]
        }

    @staticmethod
    async def get_coverage_analytics(db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Calculates matrix coverage percentage, detected techniques, and frequency metrics.
        """
        # 1. Collect covered techniques from active detection rules
        covered_techniques: Dict[str, List[str]] = defaultdict(list)
        for rule in detection_registry.get_all_rules():
            for tech in rule.mitre_techniques:
                covered_techniques[tech].append(rule.rule_id)

        # 2. Collect observed techniques from incidents in DB
        observed_technique_counts: Dict[str, int] = defaultdict(int)
        if db:
            query = select(Incident.feature_payload).where(Incident.feature_payload.isnot(None)).limit(100)
            res = await db.execute(query)
            for payload in res.scalars().all():
                if isinstance(payload, dict) and "mitre_techniques" in payload:
                    for t in payload["mitre_techniques"]:
                        observed_technique_counts[t] += 1

        total_catalog = len(MITRE_ENTERPRISE_CATALOG)
        total_covered = len(covered_techniques)
        coverage_pct = round((total_covered / max(total_catalog, 1)) * 100.0, 2)

        covered_details = []
        for tech_id, rule_ids in covered_techniques.items():
            meta = MITRE_ENTERPRISE_CATALOG.get(tech_id, {"name": "Custom Technique", "tactic": "Detection"})
            covered_details.append({
                "technique_id": tech_id,
                "name": meta["name"],
                "tactic": meta["tactic"],
                "mapped_rules_count": len(rule_ids),
                "mapped_rules": rule_ids,
                "incident_observation_count": observed_technique_counts.get(tech_id, 0)
            })

        uncovered = [
            {"technique_id": tid, "name": meta["name"], "tactic": meta["tactic"]}
            for tid, meta in MITRE_ENTERPRISE_CATALOG.items()
            if tid not in covered_techniques
        ]

        return {
            "total_catalog_techniques": total_catalog,
            "covered_techniques_count": total_covered,
            "coverage_percentage": coverage_pct,
            "covered_techniques": covered_details,
            "uncovered_techniques_count": len(uncovered),
            "uncovered_techniques": uncovered,
            "highest_frequency_detected": sorted(
                covered_details,
                key=lambda x: (x["incident_observation_count"], x["mapped_rules_count"]),
                reverse=True
            )[:5]
        }
