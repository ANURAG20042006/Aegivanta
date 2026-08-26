# AEGIVANTA ENVIRONMENT SEPARATION & FAIL-CLOSED POLICY

**Authoritative Specification**: `docs/ENVIRONMENT_SEPARATION.md`  
**Version**: 1.0.0  
**Status**: ACTIVE  

---

## 1. Supported Environment Model

Aegivanta strictly operates within one of three mutually exclusive environments defined by the authoritative environment variable:

```bash
AEGIVANTA_ENVIRONMENT = "DEMO" | "LAB" | "PRODUCTION"
```

| Dimension | DEMO | LAB | PRODUCTION |
| :--- | :--- | :--- | :--- |
| **Primary Purpose** | Sales presentations, interactive UI walkthroughs, training | Research, ML benchmarking, offline evaluation | Real-world operational cybersecurity telemetry & response |
| **Telemetry Allowed** | Synthetic, replay, mock, demo | Benchmark captures (`CICIoT2023`, `CSE-CIC-IDS2018`), test datasets | **Verified real-world sensor telemetry only** |
| **Billing Provider** | `MockBillingProvider` permitted | `MockBillingProvider` permitted | **Real commercial gateway only** (Stripe/Chargebee) |
| **CTI Feeds** | Demo/mock indicators permitted | Benchmark/research indicators permitted | **Authentic threat feeds with timestamps & source** |
| **Hunting Engine** | Seeded/demo findings permitted | Benchmark query evaluations permitted | **Real database-backed historical event search only** |
| **Dashboard Metrics** | Seeded demo KPIs permitted | Experiment benchmark metrics permitted | **Strict real-time database aggregations (0.0 / NO_DATA on empty)** |
| **ML Artifacts** | Unverified / demo models permitted | Experimental model pipelines permitted | **Strict SHA-256 cryptographically verified manifests only** |
| **Database** | SQLite / Local memory permitted | SQLite / Local PostgreSQL permitted | **Production PostgreSQL only (SQLite prohibited)** |

---

## 2. Fail-Closed Policy & Guarantees

### **"Production fails closed when provenance cannot be established."**

Under no circumstances does Aegivanta in `PRODUCTION` mode silently downgrade or fall back to `DEMO`, `LAB`, `MOCK`, `SYNTHETIC`, `SEED`, or `FIXTURE` data.

```
Incoming Operational Data / Provider
               │
               ▼
   [ Is AEGIVANTA_ENVIRONMENT == PRODUCTION? ]
        ├── NO  ──► Allow DEMO / LAB data with explicit provenance tagging
        └── YES ──► Check DataProvenance & Production Guard
                         ├── Verified Real Production Provenance ──► ACCEPT & PROCESS
                         └── Synthetic / Mock / Demo / Unverified ─► REJECT & FAIL CLOSED
                                                                           │
                                                                           ▼
                                                              Emit Security Audit Event
```

---

## 3. Data Provenance Metadata Schema

Every operational event, telemetry batch, CTI record, and ML artifact must carry explicit provenance tracking:

```json
{
  "environment": "PRODUCTION",
  "source_type": "SENSOR_EDR",
  "source_id": "sensor-node-042",
  "is_synthetic": false,
  "is_mock": false,
  "is_simulated": false,
  "is_seeded": false,
  "is_demo": false,
  "is_production": true,
  "created_at": "2026-08-26T22:45:00Z",
  "provenance_id": "prov_a9f8b2c4e1"
}
```

---

## 4. Production Security Violation Audit Trail

When a runtime guard blocks non-production data, a structured security violation event is immediately recorded in the tamper-evident audit log:

```json
{
  "timestamp": "2026-08-26T22:45:10Z",
  "environment": "PRODUCTION",
  "component": "TELEMETRY_INGESTION",
  "source": "sensor-node-042",
  "reason": "Synthetic or mock telemetry payload rejected in PRODUCTION environment.",
  "decision": "BLOCKED",
  "request_id": "req_88f910a2b"
}
```
