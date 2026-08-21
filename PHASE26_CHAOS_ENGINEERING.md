# Aegivanta — Security Chaos Engineering & Fault Injection (Phase 26.12)

## Supported Failure Scenarios

The platform includes non-destructive chaos engineering simulations to validate resilience, graceful degradation, and data-loss prevention:

1. **Redis Broker Outage (`REDIS_OUTAGE`)**: Connection refusal during event publishing triggers immediate fallback to local in-memory ring buffer.
2. **Database Query Latency Injection (`DATABASE_LATENCY`)**: Injects 5,000ms artificial query delay; connection pool rejects long-running queries gracefully with HTTP 503 instead of hanging.
3. **Worker Daemon Crash (`WORKER_CRASH`)**: Worker SIGKILL simulation; standby worker claims abandoned stream pending entries via `XAUTOCLAIM` within 30s.
4. **Telemetry Burst Surge (`TELEMETRY_BACKLOG_SURGE`)**: 50,000 EPS surge triggers sliding-window rate limit backpressure without dropping verified events.
5. **Sensor Fleet Network Partition (`SENSOR_NETWORK_PARTITION`)**: Edge sensors switch to offline SQLite disk buffering without telemetry drop.
6. **Downstream Webhook Target Failure (`WEBHOOK_DELIVERY_FAILURE`)**: Webhook platform executes 3 exponential retries with jitter then routes failed deliveries to the Dead-Letter Queue (DLQ).
7. **ML Inference Worker Timeout (`ML_INFERENCE_TIMEOUT`)**: CatBoost inference timeout triggers fallback to deterministic AST detection rules with zero packet loss.
8. **Billing Provider API Outage (`BILLING_SERVICE_OUTAGE`)**: Billing timeout activates cached entitlement grace period (72 hours).
