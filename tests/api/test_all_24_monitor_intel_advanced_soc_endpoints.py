"""
tests/api/test_all_24_monitor_intel_advanced_soc_endpoints.py
============================================================
Comprehensive test suite testing all endpoints backing the 24 navigation items
across Monitor, Intelligence, Advanced SOC, and Production Intel:
  - Dashboard
  - Live alerts
  - Protected assets
  - Asset health
  - Threat intel
  - Investigations
  - Model insights
  - AI Security Copilot
  - Threat Hunting
  - Predictive Risk
  - Threat Graph
  - ATT&CK Matrix
  - SOC Analytics
  - Detection Quality
  - Alert Queue
  - Security ROI & Value
  - Telemetry Costs
  - ML Benchmarks
  - AI Security Intel
  - Cloud & Containers
  - Endpoint XDR
  - Integrations
  - Global Operations
  - SOC Center V2
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from backend.app.main import app, initialize_application
from backend.app.database import AsyncSessionFactory
from backend.app.models.user import User
from backend.app.models.tenant import Organization, Tenant, TenantMembership
from backend.app.security import create_access_token, hash_password


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_test_environment():
    """Initializes DB schema and seeds baseline admin, tenant, and org."""
    await initialize_application()
    async with AsyncSessionFactory() as db:
        admin = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
        if not admin:
            admin = User(
                username="admin",
                email="admin@sentinelai.io",
                hashed_password=hash_password("SentinelAI@2026!Admin"),
                role="admin",
                is_active=True
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)

        org = (await db.execute(select(Organization).where(Organization.id == "default-org"))).scalar_one_or_none()
        if not org:
            org = Organization(
                id="default-org",
                name="Default Organization",
                slug="default-org",
                billing_email="admin@sentinelai.io",
                plan_tier="ENTERPRISE"
            )
            db.add(org)
            await db.commit()

        tenant = (await db.execute(select(Tenant).where(Tenant.id == "default-tenant"))).scalar_one_or_none()
        if not tenant:
            tenant = Tenant(
                id="default-tenant",
                organization_id="default-org",
                name="Default Production Tenant",
                slug="default-tenant",
                environment_type="PRODUCTION",
                is_active=True
            )
            db.add(tenant)
            await db.commit()

        membership = (await db.execute(
            select(TenantMembership).where(
                TenantMembership.user_id == admin.id,
                TenantMembership.tenant_id == "default-tenant"
            )
        )).scalar_one_or_none()
        if not membership:
            membership = TenantMembership(
                user_id=admin.id,
                tenant_id="default-tenant",
                organization_id="default-org",
                role="OWNER",
                status="ACTIVE"
            )
            db.add(membership)
            await db.commit()


@pytest.fixture
def auth_headers():
    token = create_access_token(subject="admin", role="admin")
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": "default-tenant"
    }


# ==============================================================================
# GROUP 1: MONITOR (Dashboard, Live Alerts, Protected Assets, Asset Health)
# ==============================================================================

@pytest.mark.asyncio
async def test_monitor_dashboard_overview(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200
        assert "total_incidents" in resp.json()


@pytest.mark.asyncio
async def test_monitor_live_alerts(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/alerts", headers=auth_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()


@pytest.mark.asyncio
async def test_monitor_protected_assets(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/assets", headers=auth_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()


@pytest.mark.asyncio
async def test_monitor_asset_health_summary(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/assets/summary/stats", headers=auth_headers)
        assert resp.status_code == 200
        assert "total_assets" in resp.json()


# ==============================================================================
# GROUP 2: INTELLIGENCE (Threat Intel, Investigations, Model Insights)
# ==============================================================================

@pytest.mark.asyncio
async def test_intelligence_threat_intel_iocs(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/threat-intel/iocs", headers=auth_headers)
        assert resp.status_code == 200
        assert "items" in resp.json() or isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_intelligence_investigations(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/investigations", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_intelligence_model_insights(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/analytics/summary", headers=auth_headers)
        assert resp.status_code == 200
        assert "total_packets_inspected" in resp.json() or "total_threats_detected" in resp.json()


# ==============================================================================
# GROUP 3: ADVANCED SOC (Copilot, Hunting, Predictive, Graph, ATT&CK, SOC Analytics)
# ==============================================================================

@pytest.mark.asyncio
async def test_advanced_soc_copilot_query(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/copilot/query",
            json={"query": "Summarize recent high severity threats"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        assert "response" in resp.json() or "summary" in resp.json() or "explanation" in resp.json() or "answer" in resp.json()


@pytest.mark.asyncio
async def test_advanced_soc_threat_hunting(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/hunting/saved", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_advanced_soc_predictive_risk(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/predictive/volume", headers=auth_headers)
        assert resp.status_code == 200
        assert "predicted_alert_count" in resp.json()


@pytest.mark.asyncio
async def test_advanced_soc_threat_graph(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/threat-graph", headers=auth_headers)
        assert resp.status_code == 200
        assert "nodes" in resp.json()


@pytest.mark.asyncio
async def test_advanced_soc_attack_matrix(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/attack-coverage", headers=auth_headers)
        assert resp.status_code == 200
        assert "coverage_percentage" in resp.json()


@pytest.mark.asyncio
async def test_advanced_soc_analytics_overview(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/soc-metrics/overview", headers=auth_headers)
        assert resp.status_code == 200
        assert "time_window_days" in resp.json() or "total_incidents" in resp.json() or "sample_incidents_count" in resp.json()


# ==============================================================================
# GROUP 4: PRODUCTION INTEL (Detection Quality, Alert Queue, Value, Telemetry, ML, AI Intel, Cloud, XDR, Integrations, Global Ops, SOC V2)
# ==============================================================================

@pytest.mark.asyncio
async def test_prod_intel_detection_quality(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/detection/quality", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_alert_queue_priority(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/alerts/groups/active", headers=auth_headers)
        assert resp.status_code in [200, 404]


@pytest.mark.asyncio
async def test_prod_intel_security_value(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/analytics/security-value", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_telemetry_cost(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/telemetry/cost-intelligence", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_ml_benchmarks(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/detection/benchmarks", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_ai_security_intel(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/ai-intel/models", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_cloud_security(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/cloud-security/cnapp/summary", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_endpoint_xdr(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/endpoint-xdr/telemetry", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_integrations(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/integrations", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_prod_intel_global_ops(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/global-ops/finops", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_prod_intel_soc_v2(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/soc/cases", headers=auth_headers)
        assert resp.status_code == 200
