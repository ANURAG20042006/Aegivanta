"""
backend/app/api/v1/integration_ecosystem.py
============================================
Phase 23 Enterprise Integration Ecosystem API Router.
Connector Registry, Event Bus, Webhook Platform, Integration Marketplace.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.services.connector_sdk_service import ConnectorSDKService
from backend.app.services.webhook_platform_service import WebhookPlatformService
from backend.app.observability import metrics

router = APIRouter(prefix="/integrations", tags=["Phase 23 - Enterprise Integration Ecosystem"])


class RegisterConnectorRequest(BaseModel):
    name: str = Field(..., example="Splunk Enterprise SIEM")
    connector_type: str = Field(..., example="SIEM")
    vendor: str = Field(..., example="Splunk Enterprise Security")
    auth_type: str = Field(..., example="API_KEY")
    config_encrypted: Dict[str, Any] = Field(default_factory=dict, example={"credential_ref": "vault://secrets/connector/splunk"})
    rate_limit_per_minute: int = Field(default=60)
    retry_max_attempts: int = Field(default=3)


class WebhookDeliveryTestRequest(BaseModel):
    connector_id: str
    event_id: str
    endpoint_url: str
    http_status_code: int = Field(default=200)


@router.get("/marketplace/catalog")
async def get_integration_catalog():
    """Returns the full Integration Marketplace connector catalog."""
    catalog = ConnectorSDKService.get_connector_catalog()
    metrics.aegivanta_integration_connectors_total.set(len(catalog))
    return catalog


@router.get("/connectors")
async def list_connectors(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists all registered connectors for the tenant."""
    connectors = await ConnectorSDKService.list_connectors(db=db, tenant_id=tenant_id)
    metrics.aegivanta_integration_connectors_total.set(len(connectors))
    return connectors


@router.post("/connectors/register")
async def register_connector(
    req: RegisterConnectorRequest,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Registers a new integration connector (no credentials in response)."""
    result = await ConnectorSDKService.register_connector(
        db=db,
        tenant_id=tenant_id,
        name=req.name,
        connector_type=req.connector_type,
        vendor=req.vendor,
        auth_type=req.auth_type,
        config_encrypted=req.config_encrypted,
        rate_limit_per_minute=req.rate_limit_per_minute,
        retry_max_attempts=req.retry_max_attempts
    )
    return result


@router.get("/webhooks/deliveries")
async def list_webhook_deliveries(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists webhook delivery history, failures, and dead-letter queue entries."""
    deliveries = await WebhookPlatformService.list_delivery_status(db=db, tenant_id=tenant_id)
    dead_letter_count = sum(1 for d in deliveries if d["is_dead_letter"])
    metrics.aegivanta_webhook_dead_letter_events_total.set(dead_letter_count)
    return deliveries


@router.post("/webhooks/test-delivery")
async def test_webhook_delivery(
    req: WebhookDeliveryTestRequest,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Records a simulated webhook delivery attempt for testing."""
    result = await WebhookPlatformService.record_delivery_attempt(
        db=db,
        tenant_id=tenant_id,
        connector_id=req.connector_id,
        event_id=req.event_id,
        endpoint_url=req.endpoint_url,
        hmac_signature="test_sig_" + req.event_id,
        replay_nonce=__import__("uuid").uuid4().hex,
        http_status_code=req.http_status_code,
        response_body="Simulated delivery response"
    )
    return result


@router.get("/health/dashboard")
async def get_integration_health_dashboard(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Returns connector health scores and delivery statistics dashboard."""
    connectors = await ConnectorSDKService.list_connectors(db=db, tenant_id=tenant_id)
    deliveries = await WebhookPlatformService.list_delivery_status(db=db, tenant_id=tenant_id)

    healthy = [c for c in connectors if c["health_score"] >= 80]
    degraded = [c for c in connectors if 50 <= c["health_score"] < 80]
    critical = [c for c in connectors if c["health_score"] < 50]
    dead_letters = [d for d in deliveries if d["is_dead_letter"]]

    return {
        "total_connectors": len(connectors),
        "healthy_connectors": len(healthy),
        "degraded_connectors": len(degraded),
        "critical_connectors": len(critical),
        "total_deliveries": len(deliveries),
        "dead_letter_count": len(dead_letters),
        "delivery_success_rate": (
            round((len(deliveries) - len([d for d in deliveries if d["status"] == "FAILED"])) / len(deliveries) * 100, 1)
            if deliveries else 100.0
        ),
        "connectors": connectors,
        "recent_dead_letters": dead_letters[:5]
    }
