# SentinelAI REST API & WebSockets Contract Specification

Base URL: `http://localhost:8000/api/v1`

---

## 1. Authentication Endpoints

### POST `/auth/login`
Authenticates user credentials and returns a signed JWT bearer token.

- **Request Format**: `application/x-www-form-urlencoded`
- **Fields**: `username`, `password`
- **Response HTTP 200 OK**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in_minutes": 480,
  "user_id": "8f2a1b34-...",
  "username": "admin",
  "role": "admin"
}
```

### POST `/auth/register`
Registers a new user account.

- **Request Payload**:
```json
{
  "username": "analyst_jane",
  "email": "jane@sentinelai.io",
  "password": "SecurePassword123!",
  "full_name": "Jane Doe",
  "role": "analyst"
}
```

---

## 2. Prediction Endpoints

### POST `/predict/single`
Evaluates a single network packet feature vector. Requires Bearer Token.

- **Request Payload**:
```json
{
  "features": {
    "source_ip": "192.168.1.105",
    "destination_ip": "10.0.0.1",
    "source_port": 443,
    "destination_port": 80,
    "protocol": "TCP",
    "flow_duration": 120500.0,
    "syn_flag_count": 1.0,
    "flow_packets_s": 1500.0,
    "packet_length_mean": 512.0
  },
  "model_name": "Random Forest"
}
```
- **Response HTTP 200 OK**:

> **Note**: Numeric values below (`confidence_score`, `attack_probabilities`) are **illustrative only**.
> Actual values are always derived from live `model.predict_proba()` inference on the submitted feature vector.
> `confidence_score` will be `null` if the active model does not support probability outputs.

```json
{
  "incident_id": "c9a4b2e1-...",
  "source_ip": "192.168.1.105",
  "destination_ip": "10.0.0.1",
  "attack_type": "DDoS",
  "confidence_score": "<float | null — from predict_proba()>",
  "is_malicious": true,
  "severity": "Critical",
  "model_used": "Random Forest",
  "timestamp": "2026-08-05T12:00:00Z",
  "attack_probabilities": {
    "BENIGN": "<float — from predict_proba()>",
    "DDoS": "<float — from predict_proba()>"
  },
  "shap_explanation": {
    "flow_packets_s": 0.42,
    "packet_length_mean": 0.28
  }
}
```

### POST `/predict/csv`
Ingests multi-row network traffic CSV capture file.

- **Request Format**: `multipart/form-data`
- **Fields**: `file` (CSV File), `model_name` (optional)

---

## 3. Analytics Endpoints

### GET `/analytics/summary`
Returns real-time threat summary metrics, attack distributions, and top malicious source IPs.

---

## 4. Reports & Export

### POST `/reports/generate`
Generates downloadable executive threat reports.

- **Payload**: `{"format": "pdf", "include_shap_charts": true}`
- **Response**: `{"download_url": "/api/v1/reports/download/report_123.pdf"}`

---

## 5. WebSockets Stream Endpoint

### WS `/ws/threats`
Real-time WebSocket endpoint pushing live packet flow telemetry objects every 1.5 seconds.
