import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_auth_headers(role: str = "admin") -> dict:
    env_map = {
        "admin": "SENTINEL_ADMIN_PASSWORD",
        "analyst": "SENTINEL_ANALYST_PASSWORD",
        "viewer": "SENTINEL_VIEWER_PASSWORD"
    }
    password = os.getenv(env_map.get(role, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    res = client.post("/api/v1/auth/login", data={"username": role, "password": password})
    assert res.status_code == 200, f"Login failed for {role}: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_api_lateral_movement_detect_explicit_payload():
    """Verify POST /api/v1/threat-graph/lateral-movement/detect with explicit events."""
    payload = {
        "events": [
            {
                "id": "e1",
                "source_ip": "10.10.1.5",
                "destination_ip": "10.10.1.10",
                "destination_port": 22,
                "protocol": "TCP",
                "timestamp": "2026-08-20T10:00:00Z",
                "risk_score": 70.0,
                "severity": "HIGH"
            },
            {
                "id": "e2",
                "source_ip": "10.10.1.10",
                "destination_ip": "10.10.1.20",
                "destination_port": 445,
                "protocol": "TCP",
                "timestamp": "2026-08-20T10:20:00Z",
                "risk_score": 85.0,
                "severity": "CRITICAL"
            }
        ],
        "max_dwell_hours": 24.0,
        "min_chain_length": 2
    }

    res = client.post("/api/v1/threat-graph/lateral-movement/detect", json=payload, headers=get_auth_headers("admin"))
    assert res.status_code == 200
    data = res.json()
    assert data["total_chains_detected"] >= 1
    assert len(data["chains"]) >= 1
    chain = data["chains"][0]
    assert chain["initial_compromise_host"] == "10.10.1.5"
    assert chain["target_host"] == "10.10.1.20"
    assert chain["hop_count"] == 2


@pytest.mark.integration
def test_api_chokepoints_endpoint():
    """Verify GET /api/v1/threat-graph/chokepoints returns ranked bridge nodes."""
    res = client.get("/api/v1/threat-graph/chokepoints?limit=5", headers=get_auth_headers("analyst"))
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "node_id" in data[0]
        assert "degree_centrality" in data[0]
        assert "isolation_priority" in data[0]


@pytest.mark.integration
def test_api_graph_analytics_endpoint():
    """Verify GET /api/v1/threat-graph/analytics returns topological metrics."""
    res = client.get("/api/v1/threat-graph/analytics", headers=get_auth_headers("viewer"))
    assert res.status_code == 200
    data = res.json()
    assert "total_nodes" in data
    assert "total_edges" in data
    assert "graph_density" in data
    assert "average_degree" in data


@pytest.mark.integration
def test_api_blast_radius_endpoint():
    """Verify POST /api/v1/threat-graph/blast-radius computes reachability."""
    # First query graph topology to get an existing node
    headers = get_auth_headers("admin")
    top_res = client.get("/api/v1/threat-graph", headers=headers)
    assert top_res.status_code == 200
    top_data = top_res.json()

    if top_data["nodes"]:
        first_node_id = top_data["nodes"][0]["id"]
        res = client.post(
            "/api/v1/threat-graph/blast-radius",
            json={"origin_node_id": first_node_id, "max_depth": 3},
            headers=headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["origin_node_id"] == first_node_id
        assert "blast_radius_score" in data
        assert "crown_jewel_exposure_index" in data
