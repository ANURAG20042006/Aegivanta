# SentinelAI Phase 4 — Commercial Billing & Subscriptions

## 1. Plan Comparison Matrix

| Capability / Resource | FREE Tier | PROFESSIONAL | BUSINESS | ENTERPRISE |
|---|---|---|---|---|
| **Price** | $0 / month | $499 / month | $1,499 / month | $4,999 / month |
| **Included Seats** | 3 Users | 10 Users | 25 Users | Unlimited |
| **Telemetry Quota** | 5 GB / month | 50 GB / month | 250 GB / month | 5 TB / month |
| **Retention Window** | 7 Days | 30 Days | 90 Days | 365 Days |
| **Sensors Allowed** | 2 Agents | 25 Agents | 100 Agents | Unlimited |
| **Detection Rules & IOCs** | Basic Rules | Full Feeds + Cache | Full Feeds + Cache | Full Feeds + Cache |
| **Attack Graph Analytics** | ❌ | ✅ | ✅ | ✅ |
| **Threat Hunting & Workbench** | ❌ | ❌ | ✅ | ✅ |
| **Autonomous SOAR Response** | ❌ | ❌ | ✅ | ✅ |
| **Customer API Keys** | ❌ | ❌ | ✅ | ✅ |
| **SIEM & Slack Connectors** | ❌ | ❌ | ✅ | ✅ |
| **Adaptive ML Intelligence** | ❌ | ❌ | ❌ | ✅ |
| **Dedicated Worker Cluster** | ❌ | ❌ | ❌ | ✅ |
| **Enterprise SSO (SAML/OIDC)** | ❌ | ❌ | ❌ | ✅ |

---

## 2. Webhook Architecture

- Providers: `BillingProvider` interface implemented by `MockBillingProvider` and `StripeCompatibleProvider`.
- Cryptographic Signature: Verified via HMAC-SHA256 (`Sentinel-Signature` or `Stripe-Signature`).
- Idempotency: All processed events stored in `billing_webhook_events` with unique event ID constraint to prevent duplicate processing or replay attacks.
