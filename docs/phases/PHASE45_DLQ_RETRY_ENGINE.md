# PHASE 45 — DEAD-LETTER QUEUE & RETRY ENGINE SPECIFICATION

## 1. Retry Strategy

- Failed webhook deliveries (HTTP 5xx, timeouts) retry up to 5 times using exponential backoff with decorrelated full jitter:
$$ t_{\text{backoff}} = \min(t_{\text{max}}, 2^{\text{attempt}} \times \text{base\_delay} + \text{jitter}) $$
- Unrecoverable events transition into the Dead-Letter Queue (DLQ) buffer for manual replay or forensic debugging.
