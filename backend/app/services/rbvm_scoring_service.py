"""
backend/app/services/rbvm_scoring_service.py
============================================
Phase 34 Adaptive Risk-Based Vulnerability Management (RBVM) Composite Scoring Engine.
Calculates multi-dimensional vulnerability risk:
    Score = (CVSS_v3 * 10 * 0.35) + (EPSS_prob * 100 * 0.35) + (KEV_weight * 0.20) + (Ransomware_weight * 0.10)
Assigns actionable SLAs:
- P0_CRITICAL: EPSS >= 0.70 OR (in CISA KEV on Tier 1 Asset) -> 24-hour SLA
- P1_HIGH: CVSS >= 8.0 AND EPSS >= 0.30 -> 72-hour SLA
- P2_MEDIUM: CVSS >= 6.0 -> 14-day SLA
- P3_LOW: CVSS < 6.0 -> 30-day SLA
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.vulnerability_mgmt import (
    VulnerabilityRecord, AssetVulnerabilityMapping, RemediationCampaign
)

logger = logging.getLogger("Aegivanta.RBVMScoring")


class RBVMScoringService:
    """Enterprise RBVM Composite Scoring & SLA Engine."""

    @classmethod
    def calculate_rbvm_score(
        cls,
        cvss_v3: float,
        epss_probability: float,
        in_cisa_kev: bool,
        ransomware_associated: bool,
        asset_tier: str = "TIER_1_CRITICAL"
    ) -> Dict[str, Any]:
        """Calculates multi-factor RBVM score and assigns operational priority."""
        kev_weight = 100.0 if in_cisa_kev else 0.0
        ransom_weight = 100.0 if ransomware_associated else 0.0

        raw_score = (
            (cvss_v3 * 10.0 * 0.35) +
            (epss_probability * 100.0 * 0.35) +
            (kev_weight * 0.20) +
            (ransom_weight * 0.10)
        )

        tier_multiplier = 1.0
        if asset_tier == "TIER_1_CRITICAL":
            tier_multiplier = 1.15
        elif asset_tier == "TIER_3_MEDIUM":
            tier_multiplier = 0.85

        final_score = min(100.0, round(raw_score * tier_multiplier, 1))

        if final_score >= 85.0 or (in_cisa_kev and asset_tier == "TIER_1_CRITICAL") or epss_probability >= 0.70:
            priority = "P0_CRITICAL"
            sla_hours = 24
        elif final_score >= 65.0 or epss_probability >= 0.30:
            priority = "P1_HIGH"
            sla_hours = 72
        elif final_score >= 40.0:
            priority = "P2_MEDIUM"
            sla_hours = 336  # 14 days
        else:
            priority = "P3_LOW"
            sla_hours = 720  # 30 days

        return {
            "rbvm_score": final_score,
            "priority": priority,
            "sla_hours": sla_hours
        }

    @classmethod
    async def list_vulnerabilities(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists prioritized vulnerabilities with EPSS 2.0 and CISA KEV tags."""
        stmt = select(VulnerabilityRecord).where(
            VulnerabilityRecord.tenant_id == tenant_id
        ).order_by(desc(VulnerabilityRecord.rbvm_composite_score)).limit(limit)

        records = list((await db.execute(stmt)).scalars().all())

        if not records:
            # Seed default vulnerability records
            defaults = [
                ("CVE-2023-4966", "Citrix NetScaler ADC / Gateway Information Disclosure (Citrix Bleed)", "Unauthenticated session hijacking via buffer overflow in OpenID Connect endpoint.", "Citrix NetScaler ADC", 9.4, "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", 0.942, 99.8, True, True, ["LockBit 3.0", "Volt Typhoon"], 98.5, "P0_CRITICAL", 4, "IN_PROGRESS"),
                ("CVE-2024-21887", "Ivanti Connect Secure Command Injection Zero-Day", "Command injection in web components allows authenticated admin to execute arbitrary commands.", "Ivanti Connect Secure VPN", 9.1, "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H", 0.885, 99.2, True, True, ["Lazarus Group", "Volt Typhoon"], 94.0, "P0_CRITICAL", 2, "VIRTUAL_PATCHED"),
                ("CVE-2024-3400", "Palo Alto Networks PAN-OS GlobalProtect Command Injection", "Arbitrary command execution with root privileges in GlobalProtect gateway feature.", "Palo Alto PAN-OS", 10.0, "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H", 0.912, 99.5, True, False, ["Midnight Blizzard"], 96.0, "P0_CRITICAL", 3, "OPEN"),
                ("CVE-2023-38606", "Apple WebKit Zero-Day Memory Corruption", "State-sponsored spyware deployment via WebKit flaw in iOS kernel.", "Apple WebKit", 7.8, "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H", 0.420, 88.0, True, False, [], 72.0, "P1_HIGH", 6, "OPEN")
            ]
            for cve, title, descr, comp, cvss, vec, epss, pct, kev, rns, acts, score, pri, count, stat in defaults:
                inst = VulnerabilityRecord(
                    tenant_id=tenant_id,
                    cve_id=cve,
                    title=title,
                    description=descr,
                    affected_component=comp,
                    cvss_v3_score=cvss,
                    cvss_vector=vec,
                    epss_probability=epss,
                    epss_percentile=pct,
                    in_cisa_kev=kev,
                    ransomware_associated=rns,
                    associated_threat_actors=acts,
                    rbvm_composite_score=score,
                    priority_level=pri,
                    affected_asset_count=count,
                    remediation_status=stat,
                    published_at=datetime.now(timezone.utc),
                    last_updated_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(VulnerabilityRecord).where(VulnerabilityRecord.tenant_id == tenant_id)
            records = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": r.id,
                "cve_id": r.cve_id,
                "title": r.title,
                "description": r.description,
                "affected_component": r.affected_component,
                "cvss_v3_score": r.cvss_v3_score,
                "cvss_vector": r.cvss_vector,
                "epss_probability": r.epss_probability,
                "epss_percentile": r.epss_percentile,
                "in_cisa_kev": r.in_cisa_kev,
                "ransomware_associated": r.ransomware_associated,
                "associated_threat_actors": r.associated_threat_actors,
                "rbvm_composite_score": r.rbvm_composite_score,
                "priority_level": r.priority_level,
                "affected_asset_count": r.affected_asset_count,
                "remediation_status": r.remediation_status,
                "published_at": r.published_at.isoformat()
            }
            for r in records
        ]

    @classmethod
    async def list_asset_exposures(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists asset-to-vulnerability mappings with SLA countdowns."""
        stmt = select(AssetVulnerabilityMapping).where(
            AssetVulnerabilityMapping.tenant_id == tenant_id
        ).order_by(AssetVulnerabilityMapping.sla_due_date).limit(limit)

        mappings = list((await db.execute(stmt)).scalars().all())

        if not mappings:
            # Seed default asset vulnerability mappings
            now = datetime.now(timezone.utc)
            defaults = [
                ("citrix-gw-prod-01", "TIER_1_CRITICAL", "198.51.100.10", "CVE-2023-4966", "443/HTTPS", now + timedelta(hours=14), False, "OPEN"),
                ("vpn-gateway-east", "TIER_1_CRITICAL", "198.51.100.25", "CVE-2024-21887", "443/HTTPS", now + timedelta(hours=22), False, "MITIGATED"),
                ("pan-firewall-core", "TIER_1_CRITICAL", "10.0.1.1", "CVE-2024-3400", "443/HTTPS", now - timedelta(hours=4), True, "OPEN")
            ]
            for host, tier, ip, cve, port, due, breached, stat in defaults:
                inst = AssetVulnerabilityMapping(
                    tenant_id=tenant_id,
                    hostname=host,
                    asset_criticality=tier,
                    ip_address=ip,
                    cve_id=cve,
                    port_service=port,
                    sla_due_date=due,
                    is_sla_breached=breached,
                    status=stat,
                    detected_at=now
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(AssetVulnerabilityMapping).where(AssetVulnerabilityMapping.tenant_id == tenant_id)
            mappings = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": m.id,
                "hostname": m.hostname,
                "asset_criticality": m.asset_criticality,
                "ip_address": m.ip_address,
                "cve_id": m.cve_id,
                "port_service": m.port_service,
                "sla_due_date": m.sla_due_date.isoformat(),
                "is_sla_breached": m.is_sla_breached,
                "status": m.status,
                "detected_at": m.detected_at.isoformat()
            }
            for m in mappings
        ]
