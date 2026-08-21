"""
backend/app/services/connector_sdk_service.py
=============================================
Phase 23 Connector SDK — Authentication, Health Checks, Retry with Exponential Backoff, Rate Limiting.
"""

import logging
import hashlib
import hmac
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.integration_ecosystem import IntegrationConnector

logger = logging.getLogger("Aegivanta.ConnectorSDK")

CONNECTOR_CATALOG = [
    {"connector_type": "SIEM", "vendor": "Splunk Enterprise Security", "auth_type": "API_KEY", "version": "9.0"},
    {"connector_type": "SIEM", "vendor": "Microsoft Sentinel", "auth_type": "OAUTH2", "version": "2.0"},
    {"connector_type": "SOAR", "vendor": "Palo Alto XSOAR", "auth_type": "API_KEY", "version": "8.7"},
    {"connector_type": "EDR", "vendor": "CrowdStrike Falcon EDR", "auth_type": "OAUTH2", "version": "7.0"},
    {"connector_type": "EDR", "vendor": "Microsoft Defender for Endpoint", "auth_type": "OAUTH2", "version": "2.0"},
    {"connector_type": "IAM", "vendor": "Okta Identity Engine", "auth_type": "OAUTH2", "version": "1.2"},
    {"connector_type": "IAM", "vendor": "Microsoft Entra ID (Azure AD)", "auth_type": "OAUTH2", "version": "2.0"},
    {"connector_type": "TICKETING", "vendor": "ServiceNow ITSM", "auth_type": "BASIC_AUTH", "version": "2023.04"},
    {"connector_type": "TICKETING", "vendor": "Atlassian Jira Software", "auth_type": "API_KEY", "version": "9.12"},
    {"connector_type": "MESSAGING", "vendor": "Slack Enterprise Grid", "auth_type": "OAUTH2", "version": "2.0"},
    {"connector_type": "EMAIL", "vendor": "SendGrid Email API", "auth_type": "API_KEY", "version": "3.0"},
    {"connector_type": "WEBHOOK", "vendor": "Generic HMAC Webhook", "auth_type": "HMAC_WEBHOOK", "version": "1.0"},
    {"connector_type": "THREAT_INTEL", "vendor": "MISP Threat Sharing Platform", "auth_type": "API_KEY", "version": "2.4"},
    {"connector_type": "THREAT_INTEL", "vendor": "Recorded Future Intelligence API", "auth_type": "API_KEY", "version": "3.0"},
    {"connector_type": "CLOUD", "vendor": "AWS Security Hub", "auth_type": "API_KEY", "version": "2.0"},
    {"connector_type": "CLOUD", "vendor": "Google Security Command Center", "auth_type": "OAUTH2", "version": "1.0"},
    {"connector_type": "CLOUD", "vendor": "Microsoft Defender for Cloud", "auth_type": "OAUTH2", "version": "2.0"},
]


class ConnectorSDKService:
    """Creates, validates, health-checks, and manages enterprise security connectors."""

    @classmethod
    def get_connector_catalog(cls) -> List[Dict[str, Any]]:
        """Returns the full integration marketplace connector catalog."""
        return [
            {
                "connector_type": c["connector_type"],
                "vendor": c["vendor"],
                "auth_type": c["auth_type"],
                "version": c["version"],
                "description": cls._generate_description(c["connector_type"], c["vendor"])
            }
            for c in CONNECTOR_CATALOG
        ]

    @classmethod
    def _generate_description(cls, ctype: str, vendor: str) -> str:
        descriptions = {
            "SIEM": f"Forward normalized alerts and security events to {vendor} for centralized log management and correlation.",
            "SOAR": f"Trigger {vendor} playbooks and receive enrichment data from automated response workflows.",
            "EDR": f"Bidirectional EDR telemetry exchange with {vendor} — receive host events and send containment commands.",
            "IAM": f"Identity risk scoring and session revocation integration with {vendor} identity provider.",
            "TICKETING": f"Automated incident ticket creation and lifecycle management in {vendor}.",
            "MESSAGING": f"Real-time security notification delivery to {vendor} channels.",
            "EMAIL": f"Security report and alert email delivery via {vendor}.",
            "WEBHOOK": f"Generic event delivery to external systems using {vendor} HMAC-signed webhooks.",
            "THREAT_INTEL": f"Bidirectional IOC/threat actor feed ingestion and contribution via {vendor}.",
            "CLOUD": f"Cloud security posture findings and audit log ingestion from {vendor}.",
        }
        return descriptions.get(ctype, f"{vendor} integration.")

    @classmethod
    def calculate_health_score(
        cls,
        consecutive_failures: int,
        last_successful_delivery: Optional[datetime]
    ) -> float:
        """Calculates connector health score based on failure count and recency."""
        score = 100.0

        # Penalize consecutive failures
        score -= min(consecutive_failures * 15.0, 60.0)

        # Penalize stale successful delivery
        if last_successful_delivery:
            age_hours = (datetime.now(timezone.utc) - last_successful_delivery).total_seconds() / 3600
            if age_hours > 24:
                score -= min(age_hours / 24 * 5.0, 30.0)
        else:
            score -= 10.0  # Never had a successful delivery

        return max(0.0, min(100.0, score))

    @classmethod
    def compute_exponential_backoff(cls, attempt: int, base_seconds: float = 2.0) -> float:
        """Computes jittered exponential backoff delay in seconds."""
        import random
        delay = base_seconds ** attempt
        jitter = random.uniform(0, delay * 0.25)  # up to 25% jitter
        return min(delay + jitter, 3600.0)  # capped at 1 hour

    @classmethod
    def sign_webhook_payload(cls, payload_bytes: bytes, secret: str) -> str:
        """Generates HMAC-SHA256 signature for webhook payload."""
        mac = hmac.new(secret.encode(), payload_bytes, hashlib.sha256)
        return mac.hexdigest()

    @classmethod
    def verify_webhook_signature(cls, payload_bytes: bytes, secret: str, provided_sig: str) -> bool:
        """Verifies HMAC-SHA256 webhook signature using constant-time comparison."""
        expected = cls.sign_webhook_payload(payload_bytes, secret)
        return hmac.compare_digest(expected, provided_sig)

    @classmethod
    async def list_connectors(cls, db: AsyncSession, tenant_id: str) -> List[Dict[str, Any]]:
        """Lists all registered connectors for a tenant."""
        stmt = select(IntegrationConnector).where(
            IntegrationConnector.tenant_id == tenant_id
        ).order_by(desc(IntegrationConnector.created_at))

        connectors = list((await db.execute(stmt)).scalars().all())
        if not connectors:
            # Seed default marketplace connectors for the tenant
            defaults = [
                ("Splunk ES", "SIEM", "Splunk Enterprise Security", "API_KEY", "splunk.corp.internal:8089"),
                ("CrowdStrike Falcon", "EDR", "CrowdStrike Falcon EDR", "OAUTH2", "api.crowdstrike.com"),
                ("ServiceNow ITSM", "TICKETING", "ServiceNow ITSM", "BASIC_AUTH", "corp.service-now.com"),
                ("Slack SOC Alerts", "MESSAGING", "Slack Enterprise Grid", "OAUTH2", "slack.com/api"),
            ]
            for name, ctype, vendor, auth, host in defaults:
                inst = IntegrationConnector(
                    tenant_id=tenant_id,
                    name=name,
                    connector_type=ctype,
                    vendor=vendor,
                    auth_type=auth,
                    version="1.0.0",
                    status="ENABLED",
                    health_score=95.0,
                    rate_limit_per_minute=100,
                    retry_max_attempts=3,
                    backoff_base_seconds=2.0,
                    config_encrypted={"host": host, "credential_ref": "vault://secrets/connector/" + name.lower().replace(" ", "_")},
                    last_health_check=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(IntegrationConnector).where(IntegrationConnector.tenant_id == tenant_id).order_by(desc(IntegrationConnector.created_at))
            connectors = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": c.id,
                "name": c.name,
                "connector_type": c.connector_type,
                "vendor": c.vendor,
                "version": c.version,
                "status": c.status,
                "health_score": c.health_score,
                "auth_type": c.auth_type,
                "rate_limit_per_minute": c.rate_limit_per_minute,
                "retry_max_attempts": c.retry_max_attempts,
                "consecutive_failures": c.consecutive_failures,
                "last_health_check": c.last_health_check.isoformat() if c.last_health_check else None,
                "last_successful_delivery": c.last_successful_delivery.isoformat() if c.last_successful_delivery else None,
            }
            for c in connectors
        ]

    @classmethod
    async def register_connector(
        cls,
        db: AsyncSession,
        tenant_id: str,
        name: str,
        connector_type: str,
        vendor: str,
        auth_type: str,
        config_encrypted: Dict[str, Any],
        rate_limit_per_minute: int = 60,
        retry_max_attempts: int = 3
    ) -> Dict[str, Any]:
        """Registers a new connector, storing encrypted config."""
        conn = IntegrationConnector(
            tenant_id=tenant_id,
            name=name,
            connector_type=connector_type.upper(),
            vendor=vendor,
            auth_type=auth_type.upper(),
            version="1.0.0",
            status="ENABLED",
            health_score=100.0,
            config_encrypted=config_encrypted,
            rate_limit_per_minute=rate_limit_per_minute,
            retry_max_attempts=retry_max_attempts,
            backoff_base_seconds=2.0,
            consecutive_failures=0,
            last_health_check=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        db.add(conn)
        await db.flush()
        return {"id": conn.id, "status": conn.status, "name": conn.name}
