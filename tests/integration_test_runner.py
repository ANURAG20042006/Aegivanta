import asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[1]


async def run_end_to_end_integration_test():
    """
    Executes end-to-end integration tests verifying:
    1. Database schema initialization.
    2. Authentication flow & JWT token acquisition.
    3. User profile verification via /api/v1/auth/me.
    4. Threat prediction endpoint for single packet feature vector.
    5. Batch CSV traffic file upload prediction endpoint.
    6. Analytics summary endpoint computation.
    7. Executive report generation (PDF, Excel, CSV).
    """
    print("==========================================================")
    print("      SentinelAI End-to-End System Integration Test       ")
    print("==========================================================")

    print("--> 1. Initializing Async Database Tables and default records...")
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Step 2: Authentication
            print("--> 2. Testing Authentication (/api/v1/auth/login)...")
            admin_pwd = os.environ.get("SENTINEL_ADMIN_PASSWORD", "TestAdminPassword2026!")
            login_res = await client.post(
                "/api/v1/auth/login",
                data={"username": "admin", "password": admin_pwd}
            )
            assert login_res.status_code == 200, f"Login failed: {login_res.text}"
            token_data = login_res.json()
            token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"    SUCCESS: JWT Token Acquired ({token[:20]}...)")

            # Step 3: User Me Profile
            print("--> 3. Testing User Profile (/api/v1/auth/me)...")
            me_res = await client.get("/api/v1/auth/me", headers=headers)
            assert me_res.status_code == 200, f"Get me failed: {me_res.text}"
            user_info = me_res.json()
            print(f"    SUCCESS: User Verified ({user_info['username']}, Role: {user_info['role']})")

            # Step 4: Single Packet Prediction
            print("--> 4. Testing Single Packet Prediction (/api/v1/predict/single)...")
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
            result = pred_res.json()
            assert "attack_type" in result and "shap_explanation" in result, f"Unexpected threat classification: {result}"
            print(f"    SUCCESS: Real Model Prediction -> Attack: {result['attack_type']} (Confidence: {result['confidence_score']*100:.1f}%, Malicious: {result['is_malicious']})")

            # Step 5: CSV File Upload Prediction
            print("--> 5. Testing Batch CSV Upload Prediction (/api/v1/predict/csv)...")
            csv_path = PROJECT_ROOT / "backend" / "app" / "sample_traffic.csv"
            with csv_path.open("rb") as f:
                files = {"file": ("sample_traffic.csv", f.read(), "text/csv")}
            csv_res = await client.post(
            "/api/v1/predict/csv",
            files=files,
            data={"model_name": "Random Forest"},
            headers=headers
            )
            assert csv_res.status_code == 200, f"CSV prediction failed: {csv_res.text}"
            batch_info = csv_res.json()
            threat_ratio = round((batch_info['malicious_count'] / batch_info['total_records'] * 100), 2) if batch_info['total_records'] > 0 else 0
            print(f"    SUCCESS: CSV Ingested -> Total Packets: {batch_info['total_records']}, Malicious: {batch_info['malicious_count']}, Threat Ratio: {threat_ratio}%")

            blank_value_csv = (
                b"Source IP,Destination IP,Source Port,Destination Port,Protocol,Flow Duration,Flow Packets/s,Packet Length Mean\n"
                b"192.168.1.200,10.0.0.1,,80,TCP,,,\n"
            )
            blank_csv_res = await client.post(
                "/api/v1/predict/csv",
                files={"file": ("blank-values.csv", blank_value_csv, "text/csv")},
                data={"model_name": "Random Forest"},
                headers=headers,
            )
            assert blank_csv_res.status_code == 200, f"CSV blank-value fallback failed: {blank_csv_res.text}"

            # Step 6: Analytics Summary
            print("--> 6. Testing Analytics Summary (/api/v1/analytics/summary)...")
            analytics_res = await client.get("/api/v1/analytics/summary", headers=headers)
            assert analytics_res.status_code == 200, f"Analytics summary failed: {analytics_res.text}"
            summary_info = analytics_res.json()
            print(f"    SUCCESS: Network Status: {summary_info['network_status']}, Threats Logged: {summary_info['total_threats_detected']}")

            incidents_res = await client.get(
                "/api/v1/incidents",
                params={"limit": 2, "is_malicious": "true"},
                headers=headers,
            )
            assert incidents_res.status_code == 200, f"Incident search failed: {incidents_res.text}"
            incident_page = incidents_res.json()
            assert all(item["is_malicious"] for item in incident_page["items"])
            print(f"    SUCCESS: Incident Search -> {incident_page['total']} matching records")

            # Step 7: Report Generation (PDF, Excel, CSV)
            print("--> 7. Testing Report Generation (/api/v1/reports/generate)...")
            for fmt in ["pdf", "excel", "csv"]:
                report_res = await client.post(
                "/api/v1/reports/generate",
                json={"format": fmt, "include_shap_charts": True},
                headers=headers
                )
                assert report_res.status_code == 200, f"Report generation failed for {fmt}: {report_res.text}"
                rep = report_res.json()
                download_res = await client.get(rep["download_url"], headers=headers)
                assert download_res.status_code == 200, f"Report download failed for {fmt}: {download_res.text}"
                unauthenticated_download = await client.get(rep["download_url"])
                assert unauthenticated_download.status_code == 401, "Report download should require authentication."
                print(f"    SUCCESS: Generated {fmt.upper()} Report: {rep['file_name']}")

    print("==========================================================")
    print("    ALL INTEGRATION TESTS PASSED CLEANLY (100% VERIFIED)   ")
    print("==========================================================")


if __name__ == "__main__":
    asyncio.run(run_end_to_end_integration_test())
