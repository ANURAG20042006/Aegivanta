import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.soar_connector_service import SOARConnectorService


@pytest.mark.asyncio
async def test_connector_discovery_and_health_check():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p19-conn"

        connectors = await SOARConnectorService.list_connectors(db, tenant_id)
        assert len(connectors) >= 4
        assert any(c["connector_type"] == "FIREWALL" for c in connectors)

        first_id = connectors[0]["id"]
        health = await SOARConnectorService.test_connector_health(db, first_id)

        assert health is not None
        assert health["health_status"] == "HEALTHY"
        assert health["latency_ms"] > 0.0
