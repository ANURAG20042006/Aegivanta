# Aegivanta — Phase 17: Purple-Team Attack Simulation Framework

## 1. Safe Synthetic Telemetry Pipeline
Simulations inject controlled synthetic network and authentication events directly into the active detection pipeline:
- `T1110_BRUTE_FORCE`: Credential Access brute force telemetry.
- `T1059_POWERSHELL`: Execution of anomalous PowerShell script telemetry.
- `T1021_LATERAL_MOVEMENT`: Lateral SMB and RPC probing.
- `T1078_CREDENTIAL_ACCESS`: Valid account anomaly indicators.

## 2. API Endpoints
- `POST /api/v1/security/simulations`
- `GET /api/v1/security/simulations`
- `GET /api/v1/security/simulations/{id}`
