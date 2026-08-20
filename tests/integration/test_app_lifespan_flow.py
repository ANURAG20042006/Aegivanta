import os
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.anyio
async def test_app_lifespan_e2e_flow():
    """
    Boots the actual FastAPI application, triggers the lifespan setup,
    logs in as default admin, verifies user details, hits predict endpoints,
    and inspects active models.
    """
    from backend.app.database import async_engine
    await async_engine.dispose()

    try:
        async with app.router.lifespan_context(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                # 1. Test Login
                admin_pwd = os.environ["SENTINEL_ADMIN_PASSWORD"]
                login_res = await client.post(
                    "/api/v1/auth/login",
                    data={"username": "admin", "password": admin_pwd}
                )
                assert login_res.status_code == 200, f"Login failed: {login_res.text}"
                token = login_res.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                # 2. Test Get Me Profile
                me_res = await client.get("/api/v1/auth/me", headers=headers)
                assert me_res.status_code == 200, f"Get me failed: {me_res.text}"
                assert me_res.json()["username"] == "admin"
                assert me_res.json()["email"] in ["admin@aegivanta.io", "admin@sentinelai.io"]

                # 3. Test Single Prediction
                predict_payload = {
                    "features": {
                        "source_ip": "192.168.1.120",
                        "destination_ip": "10.0.0.1",
                        "source_port": 51234,
                        "destination_port": 80,
                        "protocol": "TCP",
                        "flow_duration": 500.0,
                        "syn_flag_count": 1.0,
                        "flow_packets_s": 2500.0,
                        "packet_length_mean": 48.0
                    },
                    "model_name": "Random Forest"
                }
                pred_res = await client.post("/api/v1/predict/single", json=predict_payload, headers=headers)
                assert pred_res.status_code == 200, f"Single prediction failed: {pred_res.text}"
                assert "attack_type" in pred_res.json()
                assert "shap_explanation" in pred_res.json()

                # 4. Test Model Registry List
                models_res = await client.get("/api/v1/train/models", headers=headers)
                assert models_res.status_code == 200, f"Get models failed: {models_res.text}"
                models_list = models_res.json()
                assert len(models_list) > 0
                assert any(m["model_name"] == "Random Forest" for m in models_list)
    finally:
        await async_engine.dispose()
