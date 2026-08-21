"""
backend/app/services/threat_actor_profiling_service.py
=====================================================
Phase 32 Threat Actor Intelligence & Diamond Model Attribution Service.
Profiles advanced threat groups across:
- Diamond Model: Adversary, Capability, Infrastructure, Victimology
- MITRE ATT&CK Matrix technique mappings
- Primary motivations, targeted sectors, and active campaigns
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.threat_intel_v2 import ThreatActorProfile, CampaignHeatmapItem

logger = logging.getLogger("Aegivanta.ThreatActorProfiling")


class ThreatActorProfilingService:
    """Enterprise Threat Actor Intelligence & Diamond Model Engine."""

    @classmethod
    async def list_actors(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists detailed threat actor profiles."""
        stmt = select(ThreatActorProfile).where(
            ThreatActorProfile.tenant_id == tenant_id
        ).order_by(desc(ThreatActorProfile.last_seen_at)).limit(limit)

        actors = list((await db.execute(stmt)).scalars().all())

        if not actors:
            # Seed default threat actor profiles
            defaults = [
                (
                    "APT29 (Midnight Blizzard)", ["Cozy Bear", "Nobelium", "The Dukes"], "Russia", "NATION_STATE",
                    "Espionage & IP Theft", "STRATEGIC",
                    "SVR Russian Foreign Intelligence",
                    "Custom Implants, Cloud Token Theft, OAuth App Abuse, Supply Chain Injection",
                    "Compromised Residential Routers, Fast-Flux DNS, Tor Proxies",
                    "Government, Defense, Technology, Critical Cloud Providers",
                    ["Government", "Defense", "Cloud Providers"],
                    ["T1078", "T1195.002", "T1566.001", "T1528"]
                ),
                (
                    "Volt Typhoon (Vanguard Panda)", ["BRONZE SILHOUETTE", "Dev-0391"], "China", "NATION_STATE",
                    "Pre-Positioning in Critical Infrastructure", "STRATEGIC",
                    "PLA Strategic Support Force",
                    "Living-off-the-Land (LotL), WMI, PowerShell, Router Firmware Implants",
                    "Compromised SOHO Routers (KV-Botnet), VPN Appliances",
                    "Water, Energy, Transportation, Communications Infrastructure",
                    ["Energy", "Water", "Telecom", "Transportation"],
                    ["T1059.001", "T1047", "T1078.003", "T1133"]
                ),
                (
                    "LockBit 3.0", ["LockBit Black"], "Eastern Europe", "E_CRIME",
                    "Financial Extortion & Double Extortion Ransomware", "ADVANCED",
                    "LockBit Ransomware-as-a-Service (RaaS) Cartel",
                    "Automated Data Exfiltration Stealer, Custom LockBit 3.0 Encryptor",
                    "Bulletproof Hosting, Onion Leak Sites, Cobalt Strike Teamservers",
                    "Healthcare, Manufacturing, Financial Services, Retail",
                    ["Healthcare", "Manufacturing", "Finance"],
                    ["T1486", "T1567.002", "T1059.003", "T1021.001"]
                )
            ]
            for name, aliases, country, a_type, mot, soph, adv, cap, inf, vic, sec, tech in defaults:
                inst = ThreatActorProfile(
                    tenant_id=tenant_id,
                    actor_name=name,
                    aliases=aliases,
                    country_of_origin=country,
                    actor_type=a_type,
                    primary_motivation=mot,
                    sophistication_level=soph,
                    diamond_adversary=adv,
                    diamond_capability=cap,
                    diamond_infrastructure=inf,
                    diamond_victimology=vic,
                    targeted_sectors=sec,
                    primary_mitre_techniques=tech,
                    is_active=True,
                    last_seen_at=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(ThreatActorProfile).where(ThreatActorProfile.tenant_id == tenant_id)
            actors = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": a.id,
                "actor_name": a.actor_name,
                "aliases": a.aliases,
                "country_of_origin": a.country_of_origin,
                "actor_type": a.actor_type,
                "primary_motivation": a.primary_motivation,
                "sophistication_level": a.sophistication_level,
                "diamond_model": {
                    "adversary": a.diamond_adversary,
                    "capability": a.diamond_capability,
                    "infrastructure": a.diamond_infrastructure,
                    "victimology": a.diamond_victimology
                },
                "targeted_sectors": a.targeted_sectors,
                "primary_mitre_techniques": a.primary_mitre_techniques,
                "is_active": a.is_active,
                "last_seen_at": a.last_seen_at.isoformat()
            }
            for a in actors
        ]

    @classmethod
    async def list_campaign_heatmaps(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Lists MITRE ATT&CK technique campaign heatmap entries."""
        stmt = select(CampaignHeatmapItem).where(
            CampaignHeatmapItem.tenant_id == tenant_id
        ).order_by(desc(CampaignHeatmapItem.heat_level))

        items = list((await db.execute(stmt)).scalars().all())

        if not items:
            # Seed default campaign heatmap items
            defaults = [
                ("Midnight Blizzard Cloud Infiltration", "APT29", "Initial Access", "T1195.002", "Supply Chain Compromise", 5, 98.0),
                ("Volt Typhoon Critical Infrastructure Pre-Positioning", "Volt Typhoon", "Execution", "T1059.001", "PowerShell LotL", 5, 95.0),
                ("LockBit 3.0 Double Extortion Campaign", "LockBit 3.0", "Impact", "T1486", "Data Encrypted for Impact", 4, 92.0),
                ("Midnight Blizzard OAuth Abuse", "APT29", "Credential Access", "T1528", "Steal Application Access Token", 4, 90.0)
            ]
            for camp, act, tac, tech_id, name, heat, conf in defaults:
                inst = CampaignHeatmapItem(
                    tenant_id=tenant_id,
                    campaign_name=camp,
                    threat_actor=act,
                    tactic_name=tac,
                    mitre_technique_id=tech_id,
                    technique_name=name,
                    heat_level=heat,
                    confidence_score=conf,
                    recorded_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(CampaignHeatmapItem).where(CampaignHeatmapItem.tenant_id == tenant_id)
            items = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": i.id,
                "campaign_name": i.campaign_name,
                "threat_actor": i.threat_actor,
                "tactic_name": i.tactic_name,
                "mitre_technique_id": i.mitre_technique_id,
                "technique_name": i.technique_name,
                "heat_level": i.heat_level,
                "confidence_score": i.confidence_score,
                "recorded_at": i.recorded_at.isoformat()
            }
            for i in items
        ]
