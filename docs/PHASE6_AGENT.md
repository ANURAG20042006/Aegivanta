# Aegivanta Phase 6 — Lightweight Customer Sensor Agent

## 1. Agent Architecture (`scripts/aegivanta_agent.py`)

The Aegivanta Sensor Agent is a standalone, lightweight telemetry daemon written using only the Python 3 standard library (zero external pip packages required).

### Key Features
- **Low Overhead**: Memory footprint under 25MB, CPU utilization under 1%.
- **Local In-Memory / Offline Buffering**: Retains telemetry safely during network partition events without data loss.
- **Transparent Gzip Batching**: Automatically batches and compresses events prior to dispatch.
- **Heartbeat & Telemetry Metadata**: Continuously reports queue depth, agent host metrics, and online status.

### Usage
```bash
python scripts/aegivanta_agent.py \
  --sensor-id "sen-1234-5678" \
  --token "sen_a1b2c3d4..." \
  --api-url "https://app.sentinelai.io" \
  --batch-size 50
```
