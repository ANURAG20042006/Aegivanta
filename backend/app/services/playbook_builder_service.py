"""
backend/app/services/playbook_builder_service.py
================================================
Phase 46 Visual Playbook Builder Service.
Manages DAG-based security automation workflows and template libraries.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.security_automation_studio import AutomationPlaybook, PlaybookTemplate

logger = logging.getLogger("Aegivanta.PlaybookBuilder")


class PlaybookBuilderService:
    """Visual Playbook Builder and DAG Catalog Engine."""

    @classmethod
    async def list_playbooks(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active playbooks for a tenant."""
        stmt = select(AutomationPlaybook).where(
            AutomationPlaybook.tenant_id == tenant_id
        ).order_by(desc(AutomationPlaybook.created_at)).limit(limit)

        playbooks = list((await db.execute(stmt)).scalars().all())

        if not playbooks:
            defaults = [
                ("Ransomware Containment & Host Isolation", "Isolates endpoint, disables AD account, and creates incident ticket.", "ON_ALERT", {"nodes": 5, "edges": 4}, "ACTIVE", 42),
                ("Compromised Credential Session Reaper", "Revokes active Okta/Azure sessions and triggers step-up WebAuthn MFA.", "ON_ALERT", {"nodes": 4, "edges": 3}, "ACTIVE", 89),
                ("Phishing Mailbox Auto-Purge", "Identifies malicious email headers and purges across enterprise mailboxes.", "ON_WEBHOOK", {"nodes": 6, "edges": 5}, "ACTIVE", 124)
            ]
            for name, descr, trg, graph, stat, cnt in defaults:
                inst = AutomationPlaybook(
                    tenant_id=tenant_id,
                    name=name,
                    description=descr,
                    trigger_type=trg,
                    canvas_graph_json=graph,
                    status=stat,
                    executions_count=cnt,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(AutomationPlaybook).where(AutomationPlaybook.tenant_id == tenant_id)
            playbooks = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "trigger_type": p.trigger_type,
                "canvas_graph_json": p.canvas_graph_json,
                "status": p.status,
                "executions_count": p.executions_count,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in playbooks
        ]

    @classmethod
    async def create_playbook(
        cls,
        db: AsyncSession,
        tenant_id: str,
        name: str,
        description: str,
        trigger_type: str = "ON_ALERT",
        canvas_graph_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Creates a new DAG automation playbook."""
        graph = canvas_graph_json or {
            "nodes": [
                {"id": "node-1", "type": "TRIGGER", "title": "On Alert Critical"},
                {"id": "node-2", "type": "ACTION", "title": "Contain Host Network"},
                {"id": "node-3", "type": "NOTIFICATION", "title": "Alert SOC On-Call"}
            ],
            "edges": [
                {"source": "node-1", "target": "node-2"},
                {"source": "node-2", "target": "node-3"}
            ]
        }

        playbook = AutomationPlaybook(
            tenant_id=tenant_id,
            name=name,
            description=description,
            trigger_type=trigger_type,
            canvas_graph_json=graph,
            status="ACTIVE",
            executions_count=0,
            created_at=datetime.now(timezone.utc)
        )
        db.add(playbook)
        await db.flush()

        return {
            "id": playbook.id,
            "name": playbook.name,
            "description": playbook.description,
            "trigger_type": playbook.trigger_type,
            "canvas_graph_json": playbook.canvas_graph_json,
            "status": playbook.status,
            "executions_count": playbook.executions_count,
            "created_at": playbook.created_at.isoformat() if playbook.created_at else None
        }

    @classmethod
    async def list_templates(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists pre-built turnkey automation templates."""
        stmt = select(PlaybookTemplate).where(
            PlaybookTemplate.tenant_id == tenant_id
        ).limit(limit)

        templates = list((await db.execute(stmt)).scalars().all())

        if not templates:
            defaults = [
                ("AWS GuardDuty Crypto-Mining Quarantine", "CLOUD_SECURITY", "Quarantines compromised EC2 instances and revokes AWS IAM instance profiles.", {"steps": 4}),
                ("Dark Web Leaked Credential Reset", "IDENTITY_PROTECTION", "Matches employee email in dark web feed and forces JIT password reset.", {"steps": 3}),
                ("ZTNA Lateral Movement Kill Switch", "ZERO_TRUST", "Injects eBPF microsegment block rules upon abnormal lateral SMB scans.", {"steps": 5})
            ]
            for name, cat, descr, graph in defaults:
                inst = PlaybookTemplate(
                    tenant_id=tenant_id,
                    name=name,
                    category=cat,
                    description=descr,
                    default_graph_json=graph,
                    verified=True
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(PlaybookTemplate).where(PlaybookTemplate.tenant_id == tenant_id)
            templates = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "description": t.description,
                "default_graph_json": t.default_graph_json,
                "verified": t.verified
            }
            for t in templates
        ]
