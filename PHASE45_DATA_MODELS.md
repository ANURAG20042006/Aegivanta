# PHASE 45 — DEVELOPER PLATFORM DATA MODELS

## 1. Database Entities

1. **`DeveloperApiKey` (`developer_api_keys`)**:
   - `id`, `tenant_id`, `key_name`, `key_prefix`, `key_hash`, `scopes`, `rate_limit_rpm`, `active`, `created_at`.
2. **`WebhookSubscription` (`webhook_subscriptions`)**:
   - `id`, `tenant_id`, `endpoint_url`, `subscribed_events`, `secret_token`, `active`, `retry_count_max`, `created_at`.
3. **`WebhookDeliveryLog` (`webhook_delivery_logs`)**:
   - `id`, `tenant_id`, `subscription_id`, `event_type`, `payload_json`, `response_status`, `duration_ms`, `status`, `sent_at`.
