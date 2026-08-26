# Aegivanta Phase 6 — Sensor Fleet Management & Health Index

## 1. Fleet Health Index Calculation

The fleet health index ($H$) is a derived score (0–100) calculated from:
$$H = 100 - \min(30, \text{dropped\_events} \times 2) - (\text{buffered\_events} > 1000 ? 20 : 0)$$

## 2. Sensor Token Rotation & Security
- Sensor tokens have a default 90-day lifetime (`token_expires_at`).
- Administrators can trigger automated or manual rotation via `POST /api/v1/sensors/{id}/rotate-token`.
- Plain tokens are never stored; only SHA-256 digests (`enrollment_token_hash`) are persisted.
