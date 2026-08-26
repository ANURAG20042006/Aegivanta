# AEGIVANTA — REST & WEBSOCKET API CONTRACT

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  
**Base URL**: `/api/v1`  

---

## 1. Authentication & User Management

### `POST /api/v1/auth/login`
- **Description**: Authenticates user credentials and returns JWT Bearer access token.
- **Request Body** (Form-Data): `username`, `password`
- **Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### `GET /api/v1/auth/me`
- **Description**: Retrieves authenticated user profile and permissions.
- **Headers**: `Authorization: Bearer <token>`
- **Response** (200 OK):
```json
{
  "id": "usr-01",
  "username": "admin",
  "email": "admin@aegivanta.io",
  "full_name": "System Administrator",
  "role": "admin",
  "is_active": true
}
```

---

## 2. Telemetry & AI/ML Inference

### `POST /api/v1/telemetry/ingest`
- **Description**: Ingests structured 5-tuple flow telemetry into the distributed stream with atomic deduplication.
- **Request Body**:
```json
{
  "source_ip": "192.168.1.105",
  "destination_ip": "10.0.0.1",
  "source_port": 49152,
  "destination_port": 80,
  "protocol": "TCP",
  "flow_duration": 125000.0,
  "total_fwd_packets": 25,
  "packet_length_mean": 512.4
}
```
- **Response** (200 OK):
```json
{
  "status": "QUEUED",
  "event_id": "evt-7a8b9c",
  "stream_id": "1787225424540-0",
  "dedup_hash": "a1b2c3d4..."
}
```

### `POST /api/v1/predict/single`
- **Description**: Evaluates single network flow vector against champion CatBoost classifier with TreeSHAP explainability.
- **Response** (200 OK):
```json
{
  "prediction": "DDoS",
  "is_malicious": true,
  "confidence": 0.9845,
  "severity": "CRITICAL",
  "shap_explanation": {
    "feature_importances": [
      {"feature": "flow_packets_s", "value": 3500.0, "impact": "+0.42"},
      {"feature": "syn_flag_count", "value": 1.0, "impact": "+0.31"}
    ]
  }
}
```

---

## 3. Threat Intelligence & Incident Correlation

### `GET /api/v1/threat-intel/lookup/{indicator}`
- **Description**: Queries fast in-memory IOC cache for IP, domain, or file hash reputation.
- **Response** (200 OK):
```json
{
  "indicator": "192.168.1.105",
  "indicator_type": "IPv4",
  "threat_score": 85,
  "malware_family": "Mirai",
  "confidence": 0.92,
  "matched": true
}
```

### `GET /api/v1/incidents`
- **Description**: Retrieves paginated list of correlated security incidents with risk scores.
- **Query Params**: `limit=50`, `offset=0`, `severity=CRITICAL`, `status=OPEN`
- **Response** (200 OK):
```json
{
  "total": 12,
  "items": [
    {
      "id": "inc-8842",
      "title": "Correlated Multi-Vector DDoS Wave",
      "severity": "CRITICAL",
      "status": "INVESTIGATING",
      "risk_score": 94,
      "mitre_tactics": ["TA0040 Impact"],
      "affected_asset": "Database Server Primary",
      "created_at": "2026-08-20T10:15:00Z"
    }
  ]
}
```

---

## 4. SOAR Automated Response & Rollback

### `POST /api/v1/response/execute`
- **Description**: Executes policy-governed containment action (`BLOCK_IP`, `ISOLATE_HOST`, etc.).
- **Request Body**:
```json
{
  "action_type": "BLOCK_IP",
  "target_ip": "192.168.1.105",
  "incident_id": "inc-8842",
  "dry_run": false
}
```
- **Response** (200 OK):
```json
{
  "status": "CONTAINED",
  "execution_id": "exec-9912",
  "action": "BLOCK_IP",
  "target": "192.168.1.105",
  "verified": true,
  "can_rollback": true
}
```

---

## 5. Live WebSockets

### `WSS /api/v1/websockets/threats`
- **Description**: Bidirectional real-time stream broadcasting live flow telemetry, threat alerts, and SOAR execution events.
