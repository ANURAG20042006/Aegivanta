# Aegivanta — Forensic Evidence & Chain of Custody (Phase 26.7)

## Cryptographic Evidence Ledger

Every forensic evidence artifact is cryptographically hashed with SHA-256 upon ingestion:

```json
{
  "evidence_id": "EV-9a3b-4c2d",
  "evidence_type": "PROCESS_EVENT",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "integrity_verified": true,
  "source_system": "aegivanta.edr",
  "custody_chain": [
    {"action": "COLLECTED", "actor": "EDR_AGENT", "timestamp": "2026-08-21T10:00:00Z"},
    {"action": "VERIFIED", "actor": "SYSTEM_INTEGRITY", "timestamp": "2026-08-21T10:00:01Z"}
  ]
}
```

## Anti-Tamper Verification
The `GET /api/v1/soc/evidence/{id}/verify` endpoint recalculates the SHA-256 fingerprint over the stored canonical JSON payload to guarantee zero modification.
