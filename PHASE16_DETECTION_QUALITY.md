# Aegivanta — Phase 16: Detection Quality Engine & Benchmark Specification

## 1. Quality Metrics Architecture
The Detection Quality subsystem computes tenant-isolated detection metrics:
- **Precision**: Ground-truth confirmed true positives / (true positives + false positives).
- **Recall**: Proportion of true threats captured by detection rules and ML ensemble.
- **F1 Score**: Harmonic mean of precision and recall.
- **False-Positive Rate (FPR)**: Suppressed non-malicious alerts over total background volume.
- **Mean Time to Detect (MTTD)**: Elapsed seconds from flow `first_seen` to initial detection.
- **Mean Time to Acknowledge (MTTA)**: Elapsed seconds from alert generation to analyst triage.
- **Mean Time to Respond (MTTR)**: Elapsed seconds from detection to containment / closure.

## 2. API Endpoints
- `GET /api/v1/detection/quality?lookback_days=30`
- `GET /api/v1/detection/quality/history?limit=30`
- `GET /api/v1/detection/benchmarks?limit=20`

## 3. Reproducible Benchmarking
Every benchmark run stores dataset metadata, model versions, CPU/memory telemetry, throughput (EPS), P50/P95/P99 latencies, and a cryptographic SHA-256 result signature for auditability.
