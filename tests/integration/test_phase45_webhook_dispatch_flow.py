"""
tests/integration/test_phase45_webhook_dispatch_flow.py
=======================================================
Phase 45 Webhook Subscription & Test Dispatch Flow Integration Tests.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    password = os.getenv("SENTINEL_ADMIN_PASSWORD", "TestAdminPassword2026!")
    res = client.post("/api/v1/auth/login", data={"username": "admin", "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestWebhookDispatchFlow:
    """Integration tests for creating webhook subscriptions and executing test dispatches."""

    def test_webhook_dispatch_flow(self, client, auth_headers):
        """Test subscription creation and live test dispatch."""
        # 1. Create Subscription
        sub_resp = client.post(
            "/api/v1/developer/webhooks",
            json={
                "endpoint_url": "https://webhook.site/test-endpoint",
                "subscribed_events": "alert.created,threat.blocked"
            },
            headers=auth_headers
        )
        assert sub_resp.status_code == 200
        sub_data = sub_resp.json()
        assert sub_data["active"] is True
        assert "secret_token" in sub_data

        # 2. Test Dispatch
        disp_resp = client.post(
            "/api/v1/developer/test-dispatch",
            json={
                "endpoint_url": "https://webhook.site/test-endpoint",
                "event_type": "alert.created"
            },
            headers=auth_headers
        )
        assert disp_resp.status_code == 200
        disp_data = disp_resp.json()
        assert disp_data["status"] == "DELIVERED"
        assert disp_data["hmac_signature_header"].startswith("sha256=")

        # 3. List Deliveries
        del_resp = client.get("/api/v1/developer/deliveries", headers=auth_headers)
        assert del_resp.status_code == 200
        deliveries = del_resp.json()
        assert len(deliveries) >= 1
