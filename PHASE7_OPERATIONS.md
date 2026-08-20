# Aegivanta — Phase 7: Sensor Fleet Operations Runbook

## 1. Sensor Enrollment
```bash
# Enroll a new agent daemon
curl -X POST https://api.aegivanta.io/api/v1/sensors/enroll \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "edge-sensor-01",
    "hostname": "prod-k8s-node-1",
    "ip_address": "10.100.4.15",
    "os_type": "linux",
    "sensor_type": "ENDPOINT_EDR"
  }'
```

## 2. Fleet Health Index Calculation
- **Health Score**: Dynamic 0–100 integer computed based on heartbeat recency and buffer congestion:
  - 100: Heartbeat < 60s, queue < 100 events
  - 75: Heartbeat 60s–300s
  - 25: Heartbeat 300s–900s
  - 0: Heartbeat > 900s (marked OFFLINE)
