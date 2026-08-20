# SentinelAI — Final Threat Model & Risk Assessment

## STRIDE Threat Modeling Analysis

### 1. Spoofing Identity
- **Threat**: Adversary attempts to forge JWT auth tokens or impersonate internal microservices.
- **Mitigation**: HS256/RS256 signature verification, secret rotation, short-lived tokens, non-root service accounts in Kubernetes.

### 2. Tampering with Data
- **Threat**: Adversary modifies detection records or audit history in PostgreSQL.
- **Mitigation**: HMAC-SHA256 cryptographically chained audit trails, strict ORM parameterized queries, no raw SQL.

### 3. Repudiation
- **Threat**: Malicious admin denies executing disruptive remediation action or promoting unverified ML model.
- **Mitigation**: Immutable actor attribution on all state-altering events (`user_id`, `client_ip`, `timestamp`).

### 4. Information Disclosure
- **Threat**: Sensitive credentials, database connection strings, or internal IPs leak in API error responses or logs.
- **Mitigation**: Global regex/key sanitizers on structured JSON logger and API response interceptors.

### 5. Denial of Service (DoS)
- **Threat**: Volumetric telemetry flood exhausts Redis memory or crashes workers.
- **Mitigation**: Dynamic backpressure throttling at 5,000 pending items, worker HPA autoscaling, bounded Dead-Letter Queue (DLQ).

### 6. Elevation of Privilege
- **Threat**: Analyst executes restricted Admin actions (e.g. model promotion, SOAR execution).
- **Mitigation**: FastAPI `SecurityScopes` / `require_role(["admin"])` dependency injection checking verified JWT claims.
