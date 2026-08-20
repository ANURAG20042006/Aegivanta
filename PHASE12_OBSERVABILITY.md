# Aegivanta — Phase 12: Observability & SRE Architecture

## 1. Prometheus Metrics
Exposed at `GET /metrics` in standard Prometheus text format:
- `sentinelai_api_requests_total`: Counter by method, endpoint, status code.
- `sentinelai_detections_total`: Counter by verdict, attack type.
- `sentinelai_ml_inference_latency_seconds`: Histogram of model inference duration.
- `sentinelai_redis_queue_depth`: Gauge of pending messages per stream.
- `sentinelai_response_actions_total`: Counter of automated and manual SOAR containment actions.

## 2. Structured JSON Logging & Secret Redaction
- All log records are output as single-line JSON objects with:
  `timestamp`, `service`, `request_id`, `trace_id`, `event_type`, `severity`, `message`.
- **Recursive Secret Redaction**: Automatically replaces passwords, JWTs, sensor tokens, and API keys with `[REDACTED]`.
