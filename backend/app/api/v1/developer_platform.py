"""
backend/app/api/v1/developer_platform.py
========================================
Phase 45 Developer Platform, Public Versioned API & Webhooks Engine Router.
Exposes:
- Developer Posture Scorecard
- API Key Lifecycle Management & Token Scoping
- Webhook Subscriptions & HMAC-SHA256 Delivery Logs
- Live Event Test Dispatcher
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.developer_api_key_service import DeveloperApiKeyService
from backend.app.services.webhook_dispatcher_service import WebhookDispatcherService
from backend.app.services.developer_platform_posture_service import DeveloperPlatformPostureService

router = APIRouter(prefix="/developer", tags=["Phase 45 - Developer Platform & Webhooks Engine"])


# ==================== Request Payloads ====================

class CreateApiKeyRequest(BaseModel):
    key_name: str = Field(..., example="SOAR Remediation Automation Key")
    scopes: str = Field(default="telemetry:read,alerts:write", example="telemetry:read,alerts:write")
    rate_limit_rpm: int = Field(default=1000, example=1000)


class CreateWebhookRequest(BaseModel):
    endpoint_url: str = Field(..., example="https://api.enterprise-soc.com/webhooks/aegivanta-alerts")
    subscribed_events: str = Field(default="alert.created,threat.blocked", example="alert.created,threat.blocked")


class TestDispatchWebhookRequest(BaseModel):
    endpoint_url: str = Field(..., example="https://api.enterprise-soc.com/webhooks/aegivanta-alerts")
    event_type: str = Field(default="alert.created", example="alert.created")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Developer Platform Posture Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated developer platform scorecard metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DeveloperPlatformPostureService.get_summary(db=db, tenant_id=tenant_id)


# API Keys
@router.get("/keys", summary="List Developer API Keys")
async def list_keys(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active API keys for a tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DeveloperApiKeyService.list_keys(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/keys", summary="Generate New Scoped Developer API Key")
async def create_key(
    req: CreateApiKeyRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates a new developer API key with plaintext secret."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DeveloperApiKeyService.create_key(
        db=db,
        tenant_id=tenant_id,
        key_name=req.key_name,
        scopes=req.scopes,
        rate_limit_rpm=req.rate_limit_rpm
    )


# Webhooks
@router.get("/webhooks", summary="List Webhook Subscriptions")
async def list_webhooks(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active webhook subscriptions."""
    tenant_id = context.tenant_id or "default-tenant"
    return await WebhookDispatcherService.list_subscriptions(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/webhooks", summary="Create New Webhook Subscription")
async def create_webhook(
    req: CreateWebhookRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new webhook subscription and generates an HMAC secret."""
    tenant_id = context.tenant_id or "default-tenant"
    return await WebhookDispatcherService.create_subscription(
        db=db,
        tenant_id=tenant_id,
        endpoint_url=req.endpoint_url,
        subscribed_events=req.subscribed_events
    )


@router.get("/deliveries", summary="List Webhook Delivery Logs")
async def list_deliveries(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists recent webhook delivery logs."""
    tenant_id = context.tenant_id or "default-tenant"
    return await WebhookDispatcherService.list_deliveries(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/test-dispatch", summary="Dispatch Test Webhook Event")
async def test_dispatch(
    req: TestDispatchWebhookRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Dispatches a test event with calculated HMAC signature."""
    tenant_id = context.tenant_id or "default-tenant"
    return await WebhookDispatcherService.test_dispatch(
        db=db,
        tenant_id=tenant_id,
        endpoint_url=req.endpoint_url,
        event_type=req.event_type
    )
