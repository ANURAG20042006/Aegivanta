import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def get_authenticated_headers(username: str = "admin", password: str = None) -> dict:
    if password is None:
        env_map = {
            "admin": "SENTINEL_ADMIN_PASSWORD",
            "analyst": "SENTINEL_ANALYST_PASSWORD",
            "viewer": "SENTINEL_VIEWER_PASSWORD"
        }
        password = os.getenv(env_map.get(username, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    response = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


import uuid


def test_asset_crud_and_rbac():
    admin_hdr = get_authenticated_headers("admin")
    analyst_hdr = get_authenticated_headers("analyst")
    viewer_hdr = get_authenticated_headers("viewer")

    uid = uuid.uuid4().hex[:6]
    # 1. Viewer attempts to create asset -> 403 Forbidden
    payload = {
        "name": f"E-Commerce Gateway {uid}",
        "hostname": f"checkout-{uid}.sentinelai.internal",
        "url": f"https://checkout-{uid}.sentinelai.internal",
        "ip_address": "10.0.50.15",
        "asset_type": "api",
        "environment": "production",
        "criticality": "critical",
        "status": "active",
        "description": "PCI-DSS compliant payment processing service."
    }
    res_viewer = client.post("/api/v1/assets", json=payload, headers=viewer_hdr)
    assert res_viewer.status_code == 403

    # 2. Analyst creates asset -> 201 Created
    res_analyst = client.post("/api/v1/assets", json=payload, headers=analyst_hdr)
    assert res_analyst.status_code == 201
    asset_data = res_analyst.json()
    asset_id = asset_data["id"]
    assert asset_data["name"] == payload["name"]
    assert asset_data["criticality"] == "critical"
    assert asset_data["risk_score"] == 0.0

    # 3. Viewer reads asset list -> 200 OK
    res_list = client.get("/api/v1/assets", headers=viewer_hdr)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total"] >= 1
    assert any(a["id"] == asset_id for a in list_data["items"])

    # 4. Summary Stats endpoint
    res_stats = client.get("/api/v1/assets/summary/stats", headers=viewer_hdr)
    assert res_stats.status_code == 200
    stats_data = res_stats.json()
    assert "total_assets" in stats_data
    assert "active_healthy" in stats_data

    # 5. Asset Health profile endpoint
    res_health = client.get(f"/api/v1/assets/{asset_id}/health", headers=viewer_hdr)
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["asset_id"] == asset_id
    assert "risk_tier" in health_data

    # 6. Analyst updates asset -> 200 OK
    res_update = client.put(
        f"/api/v1/assets/{asset_id}",
        json={"status": "degraded", "description": "Under high traffic load"},
        headers=analyst_hdr
    )
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "degraded"

    # 7. Analyst tries to delete asset -> 403 Forbidden (Admin only)
    res_del_analyst = client.delete(f"/api/v1/assets/{asset_id}", headers=analyst_hdr)
    assert res_del_analyst.status_code == 403

    # 8. Admin soft-deletes asset -> 204 No Content
    res_del_admin = client.delete(f"/api/v1/assets/{asset_id}", headers=admin_hdr)
    assert res_del_admin.status_code == 204

    # 9. Verify asset is deactivated (soft-deleted), not physically wiped
    res_get_deactivated = client.get(f"/api/v1/assets/{asset_id}", headers=viewer_hdr)
    assert res_get_deactivated.status_code == 200
    assert res_get_deactivated.json()["status"] == "inactive"


def test_asset_input_validation():
    admin_hdr = get_authenticated_headers("admin")

    # Invalid asset type
    res = client.post(
        "/api/v1/assets",
        json={"name": "Invalid Asset", "hostname": "invalid.local", "asset_type": "quantum_computer"},
        headers=admin_hdr
    )
    assert res.status_code == 422

    # Invalid URL scheme
    res2 = client.post(
        "/api/v1/assets",
        json={"name": "Bad URL", "hostname": "badurl.local", "url": "ftp://badurl.local"},
        headers=admin_hdr
    )
    assert res2.status_code == 422
