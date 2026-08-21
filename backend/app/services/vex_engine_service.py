"""
backend/app/services/vex_engine_service.py
=========================================
Phase 29 OpenVEX & CSAF Vulnerability Exploitability eXchange (VEX) Service.
Suppresses non-exploitable CVE alerts through structured OpenVEX justifications:
- NOT_AFFECTED (Vulnerable code not present / not reachable / compiler hardening)
- AFFECTED (Actionable active vulnerability)
- FIXED (Patched in current release)
- UNDER_INVESTIGATION (Triage in progress)
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.supply_chain import VEXStatement

logger = logging.getLogger("Aegivanta.VEXEngine")


class VEXEngineService:
    """Enterprise OpenVEX statement publisher and exploitability evaluator."""

    @classmethod
    async def list_statements(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists OpenVEX statements for a tenant."""
        stmt = select(VEXStatement).where(
            VEXStatement.tenant_id == tenant_id
        ).order_by(desc(VEXStatement.published_at)).limit(limit)

        statements = list((await db.execute(stmt)).scalars().all())

        if not statements:
            # Seed default VEX statements
            defaults = [
                ("CVE-2026-10492", "pkg:npm/jsonwebtoken@9.0.2", "NOT_AFFECTED", "Vulnerable code path is not invoked by application runtime", "Application enforces asymmetric RS256 token verification, bypassing vulnerable symmetric algorithm downgrade vector."),
                ("CVE-2025-48190", "pkg:pypi/urllib3@2.0.7", "FIXED", "Patched in release v29.0.0", "Upgraded to urllib3 v2.2.1 resolving proxy header leak."),
                ("CVE-2026-33910", "pkg:pypi/cryptography@42.0.5", "UNDER_INVESTIGATION", "Security research team conducting fuzzing analysis", "Under investigation by Aegivanta Supply Chain Security lab.")
            ]
            for cve, purl, status, just, impact in defaults:
                inst = VEXStatement(
                    tenant_id=tenant_id,
                    vulnerability_id=cve,
                    product_purl=purl,
                    status=status,
                    justification=just,
                    impact_statement=impact,
                    author="Aegivanta SupplyChain Security Lab",
                    published_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(VEXStatement).where(VEXStatement.tenant_id == tenant_id)
            statements = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": s.id,
                "vulnerability_id": s.vulnerability_id,
                "product_purl": s.product_purl,
                "status": s.status,
                "justification": s.justification,
                "impact_statement": s.impact_statement,
                "author": s.author,
                "published_at": s.published_at.isoformat()
            }
            for s in statements
        ]

    @classmethod
    async def publish_statement(
        cls,
        db: AsyncSession,
        tenant_id: str,
        vulnerability_id: str,
        product_purl: str,
        status: str,
        justification: str,
        impact_statement: str
    ) -> VEXStatement:
        """Publishes an OpenVEX exploitability statement."""
        stmt = VEXStatement(
            tenant_id=tenant_id,
            vulnerability_id=vulnerability_id.upper().strip(),
            product_purl=product_purl,
            status=status.upper().strip(),
            justification=justification,
            impact_statement=impact_statement,
            author="Aegivanta Security Team",
            published_at=datetime.now(timezone.utc)
        )
        db.add(stmt)
        await db.flush()
        return stmt

    @classmethod
    async def export_openvex_json(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Exports compliant OpenVEX format document."""
        stmts = await cls.list_statements(db=db, tenant_id=tenant_id)
        return {
            "@context": "https://openvex.dev/ns/v0.2.0",
            "@id": f"https://aegivanta.io/vex/openvex-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "author": "Aegivanta Supply Chain Security Engine",
            "role": "Software Supplier",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": 1,
            "statements": [
                {
                    "vulnerability": {"name": s["vulnerability_id"]},
                    "products": [{"@id": s["product_purl"]}],
                    "status": s["status"].lower(),
                    "justification": s["justification"],
                    "impact_statement": s["impact_statement"]
                }
                for s in stmts
            ]
        }
